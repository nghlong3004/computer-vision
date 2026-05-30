# -*- coding: utf-8 -*-
"""Captures and saves bad-posture screenshots."""

import os
import time
from datetime import datetime

import cv2


class ScreenshotService:
    """Auto-captures screenshots with cooldown between captures."""

    def __init__(self, folder="screenshots", cooldown=30):
        self._folder = folder
        self._cooldown = cooldown
        self._last_time = 0
        self.count = 0
        os.makedirs(folder, exist_ok=True)

    def capture(self, image):
        """Save screenshot if cooldown elapsed. Returns path or None."""
        if time.time() - self._last_time < self._cooldown:
            return None
        self._last_time = time.time()
        self.count += 1
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self._folder, f"bad_posture_{ts}.jpg")
        cv2.imwrite(path, image)
        print(f"  [📸] Đã chụp ảnh: {path}")
        return path
