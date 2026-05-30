# -*- coding: utf-8 -*-
"""Posture analysis — angle calculation and classification."""

import math
from dataclasses import dataclass


@dataclass
class PostureResult:
    """Analysis result for a single frame."""
    is_good: bool
    neck_angle: float
    torso_angle: float
    shoulder_offset: float
    shoulders_aligned: bool
    score: float
    coords: dict


class PostureAnalyzer:
    """Classifies posture as good/bad based on neck & torso inclination angles."""

    def __init__(self, neck_threshold=25, torso_threshold=10, offset_threshold=100):
        self.neck_threshold = neck_threshold
        self.torso_threshold = torso_threshold
        self._offset_threshold = offset_threshold

    def analyze(self, coords):
        """Analyze posture from landmark coordinates. Returns PostureResult."""
        offset = self._distance(coords["left_shoulder"], coords["right_shoulder"])
        neck = self._angle(coords["left_shoulder"], coords["left_ear"])
        torso = self._angle(coords["left_hip"], coords["left_shoulder"])

        is_good = neck < self.neck_threshold and torso < self.torso_threshold

        n_score = max(0, 100 - (neck / self.neck_threshold) * 50)
        t_score = max(0, 100 - (torso / self.torso_threshold) * 50)

        return PostureResult(
            is_good=is_good,
            neck_angle=neck,
            torso_angle=torso,
            shoulder_offset=offset,
            shoulders_aligned=offset < self._offset_threshold,
            score=min(100, (n_score + t_score) / 2),
            coords=coords,
        )

    @staticmethod
    def _distance(p1, p2):
        """Euclidean distance between two points."""
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    @staticmethod
    def _angle(p1, p2):
        """Angle between line p1->p2 and the vertical Y-axis (degrees)."""
        x1, y1 = p1
        x2, y2 = p2
        if y1 == 0:
            y1 = 1
        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if length == 0:
            return 0
        cos_t = max(-1, min(1, (y2 - y1) * (-y1) / (length * y1)))
        return int(180 / math.pi) * math.acos(cos_t)
