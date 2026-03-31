from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


class ImageIO:
    """Handle image loading and saving concerns."""

    def load(self, file_path: Path) -> np.ndarray:
        if not file_path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        image = cv2.imread(str(file_path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Cannot decode image data from: {file_path}")
        return image

    def save(self, file_path: Path, image: np.ndarray) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(file_path), image):
            raise OSError(f"Cannot save image to: {file_path}")

    def show(self, window_name: str, image: np.ndarray) -> None:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, image)
