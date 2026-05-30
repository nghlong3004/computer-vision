# -*- coding: utf-8 -*-
"""Plays warning beep sounds with cooldown."""

import time
import winsound
from threading import Thread


class AlertService:
    """Non-blocking audio alert with cooldown between triggers."""

    def __init__(self, cooldown=5):
        self._cooldown = cooldown
        self._last_time = 0

    def trigger(self):
        """Play alert if cooldown elapsed. Returns True if played."""
        if time.time() - self._last_time < self._cooldown:
            return False
        self._last_time = time.time()
        Thread(target=self._beep, daemon=True).start()
        return True

    @staticmethod
    def _beep():
        try:
            for _ in range(3):
                winsound.Beep(1000, 300)
                time.sleep(0.1)
        except Exception:
            pass
