# -*- coding: utf-8 -*-
"""Sends notifications via Telegram Bot API."""

import os
import time
from threading import Thread

import requests


class TelegramService:
    """Non-blocking Telegram message and photo sender with cooldown."""

    def __init__(self, bot_token="", chat_id="", cooldown=60):
        self._token = bot_token
        self._chat_id = chat_id
        self._cooldown = cooldown
        self._last_time = 0
        self._url = f"https://api.telegram.org/bot{bot_token}"

    @property
    def enabled(self):
        return bool(self._token and self._chat_id)

    def send_photo(self, path, caption=""):
        """Send photo if cooldown elapsed (non-blocking)."""
        if not self.enabled or time.time() - self._last_time < self._cooldown:
            return False
        self._last_time = time.time()
        Thread(target=self._do_photo, args=(path, caption), daemon=True).start()
        return True

    def send_report(self, summary, chart_path=None):
        """Send end-of-session report (blocking — called once at exit)."""
        if not self.enabled:
            return False

        d = summary["duration"]
        text = (
            "📊 *BÁO CÁO PHIÊN GIÁM SÁT TƯ THẾ*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱ Thời lượng: {d:.0f}s ({d/60:.1f} phút)\n"
            f"✅ Tư thế tốt: {summary['good_pct']:.1f}%\n"
            f"❌ Tư thế xấu: {summary['bad_pct']:.1f}%\n"
            f"📸 Frame tốt: {summary['total_good']}\n"
            f"📸 Frame xấu: {summary['total_bad']}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        self._do_message(text, parse_mode="Markdown")

        if chart_path and os.path.exists(chart_path):
            time.sleep(0.5)
            self._do_photo(chart_path, caption="Biểu đồ phiên giám sát")
        return True

    def _do_message(self, text, parse_mode=None):
        try:
            data = {"chat_id": self._chat_id, "text": text}
            if parse_mode:
                data["parse_mode"] = parse_mode
            requests.post(f"{self._url}/sendMessage", data=data, timeout=10)
        except Exception as e:
            print(f"  [Lỗi Telegram] {e}")

    def _do_photo(self, path, caption=""):
        try:
            with open(path, "rb") as f:
                requests.post(
                    f"{self._url}/sendPhoto",
                    data={"chat_id": self._chat_id, "caption": caption},
                    files={"photo": f},
                    timeout=15,
                )
        except Exception as e:
            print(f"  [Lỗi Telegram] {e}")
