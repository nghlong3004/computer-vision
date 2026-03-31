from __future__ import annotations

import random
from pathlib import Path
from typing import Iterable


class WorkspaceImageProvider:
    """Find and pick input images from a workspace."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", "outputs", "build", "dist"}

    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)

    def list_images(self, root: Path) -> list[Path]:
        if not root.exists():
            return []

        images: list[Path] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if any(part in self.EXCLUDED_DIRS for part in path.parts):
                continue

            if path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                images.append(path)

        return sorted(images)

    def pick_random(self, images: Iterable[Path]) -> Path:
        image_list = list(images)
        if not image_list:
            raise ValueError("No images found to choose from.")
        return self._random.choice(image_list)
