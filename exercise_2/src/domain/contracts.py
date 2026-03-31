from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class FilterEngine(ABC):
    """Abstraction for image filtering backends."""

    @abstractmethod
    def apply(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Apply a convolution-like filter and return a new image."""
        raise NotImplementedError
