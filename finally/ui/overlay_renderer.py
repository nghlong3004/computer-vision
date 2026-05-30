# -*- coding: utf-8 -*-
"""Draws UI overlay elements on the camera frame."""

import time
import cv2
import config as cfg


class OverlayRenderer:
    """Renders info panel, gauge, status badge, skeleton, and warnings on frame."""

    FONT = cv2.FONT_HERSHEY_SIMPLEX

    @staticmethod
    def draw_info_panel(img, lines, x=5, y=5, pad=10):
        """Semi-transparent panel with text lines. lines: [(text, color)]."""
        scale, thick, lh = 0.50, 1, 24
        max_w = max(cv2.getTextSize(t, OverlayRenderer.FONT, scale, thick)[0][0] for t, _ in lines)

        pw, ph = max_w + pad * 2, len(lines) * lh + pad * 2
        overlay = img.copy()
        cv2.rectangle(overlay, (x, y), (x + pw, y + ph), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)

        for i, (text, color) in enumerate(lines):
            cv2.putText(img, text, (x + pad, y + pad + (i + 1) * lh),
                        OverlayRenderer.FONT, scale, color, thick)

    @staticmethod
    def draw_gauge(img, score, x, y, w, h):
        """Horizontal posture score bar (0–100)."""
        cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 50), -1)
        cv2.rectangle(img, (x, y), (x + w, y + h), (180, 180, 180), 1)

        fill = int(w * max(0, min(100, score)) / 100)
        color = cfg.COLOR_GREEN if score > 70 else cfg.COLOR_YELLOW if score > 40 else cfg.COLOR_RED
        if fill > 0:
            cv2.rectangle(img, (x, y), (x + fill, y + h), color, -1)

        cv2.putText(img, f"Posture: {int(score)}%", (x + 5, y - 8),
                    OverlayRenderer.FONT, 0.55, cfg.COLOR_WHITE, 1)

    @staticmethod
    def draw_badge(img, text, color, frame_w):
        """Colored status badge at top-right corner."""
        bw, bh = 230, 45
        bx, by = frame_w - bw - 10, 10
        overlay = img.copy()
        cv2.rectangle(overlay, (bx, by), (bx + bw, by + bh), color, -1)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        cv2.putText(img, text, (bx + 12, by + 32),
                    OverlayRenderer.FONT, 0.7, (0, 0, 0), 2)

    @staticmethod
    def draw_skeleton(img, coords, line_color):
        """Draw body landmarks and connecting lines."""
        ls, rs = coords["left_shoulder"], coords["right_shoulder"]
        le, lh = coords["left_ear"], coords["left_hip"]

        for pt, c, f in [
            (ls, cfg.COLOR_WHITE, 2), (le, cfg.COLOR_WHITE, 2),
            ((ls[0], ls[1] - 100), cfg.COLOR_WHITE, 2),
            (rs, cfg.COLOR_PINK, -1),
            (lh, cfg.COLOR_YELLOW, -1),
            ((lh[0], lh[1] - 100), cfg.COLOR_YELLOW, -1),
        ]:
            cv2.circle(img, pt, 7, c, f)

        for p1, p2 in [
            (ls, le), (ls, (ls[0], ls[1] - 100)),
            (lh, ls), (lh, (lh[0], lh[1] - 100)),
        ]:
            cv2.line(img, p1, p2, line_color, 2)

    @staticmethod
    def draw_angles(img, coords, result, color):
        """Show angle values next to shoulder and hip."""
        ls, lh = coords["left_shoulder"], coords["left_hip"]
        cv2.putText(img, f"{int(result.neck_angle)} deg",
                    (ls[0] + 10, ls[1]), OverlayRenderer.FONT, 0.6, color, 2)
        cv2.putText(img, f"{int(result.torso_angle)} deg",
                    (lh[0] + 10, lh[1]), OverlayRenderer.FONT, 0.6, color, 2)

    @staticmethod
    def draw_warning(img, w, h):
        """Flashing red border + warning text."""
        if int(time.time() * 3) % 2 == 0:
            cv2.rectangle(img, (0, 0), (w - 1, h - 1), cfg.COLOR_RED, 5)
            cv2.putText(img, "!! SUA TU THE NGAY !!",
                        (w // 2 - 180, h // 2),
                        OverlayRenderer.FONT, 1.0, cfg.COLOR_RED, 3)

    @staticmethod
    def draw_no_person(img, w, h):
        """Show 'no person detected' message."""
        cv2.putText(img, "Khong phat hien nguoi...",
                    (w // 2 - 160, h // 2),
                    OverlayRenderer.FONT, 0.7, cfg.COLOR_YELLOW, 2)
