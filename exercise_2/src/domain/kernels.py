from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Kernel:
    name: str
    matrix: np.ndarray

    def vertical(self, name: str | None = None) -> "Kernel":
        """Rotate a horizontal 1D kernel into vertical orientation."""
        rotated = self.matrix.T
        return Kernel(name=name or f"{self.name}_vertical", matrix=rotated)


class KernelFactory:
    """Factory for predefined kernels required by the assignment."""

    @staticmethod
    def mean_1d_horizontal() -> Kernel:
        matrix = np.ones((1, 5), dtype=np.float32) / 5.0
        return Kernel(name="1d_mean_1x5_horizontal", matrix=matrix)

    @staticmethod
    def weighted_1d_horizontal() -> Kernel:
        matrix = np.array([[1, 2, 4, 2, 1]], dtype=np.float32)
        matrix = matrix / matrix.sum()
        return Kernel(name="1d_weighted_1x5_horizontal", matrix=matrix)

    @staticmethod
    def mean_2d() -> Kernel:
        matrix = np.ones((3, 3), dtype=np.float32) / 9.0
        return Kernel(name="2d_mean_3x3", matrix=matrix)

    @staticmethod
    def weighted_2d() -> Kernel:
        matrix = np.array(
            [
                [1, 2, 1],
                [2, 8, 2],
                [1, 2, 1],
            ],
            dtype=np.float32,
        )
        matrix = matrix / matrix.sum()
        return Kernel(name="2d_weighted_3x3", matrix=matrix)
