from __future__ import annotations

import cv2
import numpy as np

from src.domain.contracts import FilterEngine


class OpenCVFilterEngine(FilterEngine):
    """Filter engine backed by OpenCV's filter2D."""

    def apply(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        return cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
