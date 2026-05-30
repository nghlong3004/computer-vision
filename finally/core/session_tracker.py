# -*- coding: utf-8 -*-
"""Tracks frame counts and timing across a monitoring session."""

import time


class SessionTracker:
    """Counts good/bad frames, tracks streaks, and computes session stats."""

    def __init__(self):
        self.start_time = time.time()
        self._good_streak = 0
        self._bad_streak = 0
        self._total_good = 0
        self._total_bad = 0

    def update(self, is_good):
        """Update counters after each frame."""
        if is_good:
            self._bad_streak = 0
            self._good_streak += 1
            self._total_good += 1
        else:
            self._good_streak = 0
            self._bad_streak += 1
            self._total_bad += 1

    def streak_time(self, fps):
        """Returns (good_seconds, bad_seconds) for current streak."""
        fps = fps if fps > 0 else 30
        return self._good_streak / fps, self._bad_streak / fps

    def summary(self):
        """Returns session summary dict."""
        duration = time.time() - self.start_time
        total = self._total_good + self._total_bad
        good_pct = (self._total_good / total * 100) if total > 0 else 0
        return {
            "duration": duration,
            "total_good": self._total_good,
            "total_bad": self._total_bad,
            "good_pct": good_pct,
            "bad_pct": 100 - good_pct,
        }
