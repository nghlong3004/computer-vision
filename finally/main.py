# -*- coding: utf-8 -*-
"""
Posture Monitoring System — Entry Point.

Usage:
    python main.py
    python main.py --alert-time 5
    python main.py --video path/to/video.mp4
"""

import argparse
import os
import sys
import time

# Ensure Vietnamese prints correctly on Windows console
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import cv2

import config as cfg
from core import PoseDetector, PostureAnalyzer, SessionTracker
from services import AlertService, ScreenshotService, TelegramService, ReportService
from ui import OverlayRenderer


class PostureMonitor:
    """
    Main orchestrator — composes all modules and runs the monitoring loop.

    Follows the Single Responsibility Principle:
    each dependency handles exactly one concern.
    """

    def __init__(self, video_source=0, alert_time=None):
        # Core
        self._detector = PoseDetector()
        self._analyzer = PostureAnalyzer(
            cfg.NECK_ANGLE_THRESHOLD,
            cfg.TORSO_ANGLE_THRESHOLD,
            cfg.SHOULDER_OFFSET_THRESHOLD,
        )
        self._tracker = SessionTracker()

        # Services
        self._alert = AlertService(cfg.ALERT_SOUND_COOLDOWN)
        self._screenshot = ScreenshotService(cfg.SCREENSHOT_DIR, cfg.SCREENSHOT_COOLDOWN)
        self._telegram = TelegramService(cfg.TELEGRAM_BOT_TOKEN, cfg.TELEGRAM_CHAT_ID, cfg.TELEGRAM_COOLDOWN)
        self._report = ReportService(cfg.SCREENSHOT_DIR)

        # UI
        self._ui = OverlayRenderer()

        # Config
        self._source = video_source
        self._alert_time = alert_time or cfg.ALERT_TIME

    # ── Public ──

    def run(self):
        """Main monitoring loop."""
        cap = self._open_camera()
        if not cap:
            return

        self._print_header()

        while True:
            ok, frame = cap.read()
            if not ok:
                print("  [Thông báo] Hết frame.")
                break

            fps = cap.get(cv2.CAP_PROP_FPS) or cfg.DEFAULT_FPS
            h, w = frame.shape[:2]

            # Detect
            landmarks = self._detector.detect(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if landmarks is None:
                self._ui.draw_no_person(frame, w, h)
                self._ui.draw_gauge(frame, 0, 10, h - 45, w - 20, 25)
                cv2.imshow("Giam Sat Tu The", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            # Analyze
            coords = self._detector.get_all_coords(landmarks, w, h)
            result = self._analyzer.analyze(coords)
            self._tracker.update(result.is_good)
            good_t, bad_t = self._tracker.streak_time(fps)

            # Render
            self._render(frame, result, good_t, bad_t, w, h)

            # Alerts
            if bad_t > self._alert_time:
                self._handle_alert(frame, bad_t, w, h)

            cv2.imshow("Giam Sat Tu The", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        self._detector.release()
        self._end_session()

    # ── Private ──

    def _open_camera(self):
        if self._source and self._source != 0:
            cap = cv2.VideoCapture(self._source)
        else:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("  [Lỗi] Không thể mở camera!")
            return None
        return cap

    def _render(self, frame, result, good_t, bad_t, w, h):
        """Draw all UI elements on the frame."""
        color = cfg.COLOR_GREEN if result.is_good else cfg.COLOR_RED
        text_c = cfg.COLOR_LIGHT_GREEN if result.is_good else cfg.COLOR_RED

        self._ui.draw_skeleton(frame, result.coords, color)
        self._ui.draw_angles(frame, result.coords, result, text_c)

        # Build info lines
        align = (f"Vai: OK ({int(result.shoulder_offset)}px)", cfg.COLOR_GREEN) \
            if result.shoulders_aligned else \
            (f"Vai: LECH ({int(result.shoulder_offset)}px)", cfg.COLOR_RED)

        lines = [
            (f"Co:   {int(result.neck_angle)} deg (max {self._analyzer.neck_threshold})", text_c),
            (f"Lung: {int(result.torso_angle)} deg (max {self._analyzer.torso_threshold})", text_c),
            align,
        ]

        if result.is_good:
            lines.append((f"Tu the tot: {good_t:.1f}s", cfg.COLOR_GREEN))
            self._ui.draw_badge(frame, "TU THE TOT", cfg.COLOR_GREEN, w)
        else:
            lines.append((f"Tu the xau: {bad_t:.1f}s", cfg.COLOR_RED))
            self._ui.draw_badge(frame, "TU THE XAU", cfg.COLOR_RED, w)

        elapsed = int(time.time() - self._tracker.start_time)
        lines.append((f"Phien: {elapsed}s | Anh: {self._screenshot.count}", cfg.COLOR_WHITE))

        self._ui.draw_info_panel(frame, lines)
        self._ui.draw_gauge(frame, result.score, 10, h - 45, w - 20, 25)

    def _handle_alert(self, frame, bad_t, w, h):
        """Trigger sound, screenshot, telegram, and flash warning."""
        self._ui.draw_warning(frame, w, h)

        if self._alert.trigger():
            print(f"  [⚠️] Ngồi sai tư thế {bad_t:.0f}s!")

        photo = self._screenshot.capture(frame)
        if photo and self._telegram.enabled:
            self._telegram.send_photo(photo, f"⚠️ Ngồi sai tư thế đã {bad_t:.0f} giây!")

    def _end_session(self):
        """Print summary, generate chart, send Telegram report."""
        s = self._tracker.summary()
        d = s["duration"]

        print()
        print("=" * 50)
        print("       THỐNG KÊ PHIÊN GIÁM SÁT")
        print("=" * 50)
        print(f"  Thời lượng:     {d:.0f}s ({d/60:.1f} phút)")
        print(f"  Tư thế tốt:    {s['good_pct']:.1f}%  ({s['total_good']} frame)")
        print(f"  Tư thế xấu:    {s['bad_pct']:.1f}%  ({s['total_bad']} frame)")
        print(f"  Ảnh đã chụp:   {self._screenshot.count}")
        print("=" * 50)

        chart = None
        try:
            chart = self._report.generate(
                s, self._analyzer.neck_threshold, self._analyzer.torso_threshold,
                self._alert_time, self._screenshot.count,
            )
            os.startfile(os.path.abspath(chart))
        except Exception as e:
            print(f"  [Lỗi] Không tạo được biểu đồ: {e}")

        if self._telegram.enabled:
            print("  [📤] Đang gửi báo cáo qua Telegram...")
            self._telegram.send_report(s, chart)
            print("  [✅] Đã gửi!")

    def _print_header(self):
        tg = "BẬT ✅" if self._telegram.enabled else "TẮT"
        print()
        print("=" * 50)
        print("   HỆ THỐNG GIÁM SÁT TƯ THẾ NGỒI v2.0")
        print("=" * 50)
        print(f"  Nguồn video:     {self._source}")
        print(f"  Ngưỡng cổ:       {self._analyzer.neck_threshold}°")
        print(f"  Ngưỡng lưng:     {self._analyzer.torso_threshold}°")
        print(f"  Cảnh báo sau:    {self._alert_time}s")
        print(f"  Telegram:        {tg}")
        print("=" * 50)
        print("  Nhấn 'q' để thoát.\n")


# ── Entry point ──

def parse_args():
    p = argparse.ArgumentParser(description="Hệ thống giám sát tư thế ngồi")
    p.add_argument("--video", type=str, default=0, help="Video path or 0 for webcam")
    p.add_argument("--alert-time", type=int, default=None, help="Seconds before alert")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    PostureMonitor(args.video, args.alert_time).run()
