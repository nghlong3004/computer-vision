# -*- coding: utf-8 -*-
"""Wraps MediaPipe Pose to detect body landmarks."""

import mediapipe as mp


class PoseDetector:
    """Detects 33 body landmarks using MediaPipe Pose."""

    _LANDMARKS = {
        "left_shoulder": mp.solutions.pose.PoseLandmark.LEFT_SHOULDER,
        "right_shoulder": mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER,
        "left_ear": mp.solutions.pose.PoseLandmark.LEFT_EAR,
        "left_hip": mp.solutions.pose.PoseLandmark.LEFT_HIP,
    }

    def __init__(self):
        self._pose = mp.solutions.pose.Pose()

    def detect(self, rgb_image):
        """Return pose_landmarks or None if no person found."""
        return self._pose.process(rgb_image).pose_landmarks

    def get_all_coords(self, landmarks, w, h):
        """Extract pixel coordinates for all tracked landmarks."""
        return {
            name: (
                int(landmarks.landmark[lm].x * w),
                int(landmarks.landmark[lm].y * h),
            )
            for name, lm in self._LANDMARKS.items()
        }

    def release(self):
        """Release MediaPipe resources."""
        self._pose.close()
