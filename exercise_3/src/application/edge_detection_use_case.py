from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.infrastructure.image_io import ImageIO


@dataclass(frozen=True)
class EdgeDetectionConfig:
    output_dir: Path
    show_windows: bool = False
    blur_kernel_profile_1: int = 3
    canny_low_profile_1: int = 50
    canny_high_profile_1: int = 150
    blur_kernel_profile_2: int = 7
    canny_low_profile_2: int = 120
    canny_high_profile_2: int = 250


class EdgeDetectionUseCase:
    """Detect edges and draw contours with different parameter profiles."""

    def __init__(self, image_io: ImageIO) -> None:
        self._image_io = image_io

    def execute(self, input_image: np.ndarray, input_path: Path, config: EdgeDetectionConfig) -> dict[str, Path]:
        gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

        edges_1, contour_1, contour_count_1 = self._run_profile(
            image=input_image,
            gray=gray,
            blur_kernel=config.blur_kernel_profile_1,
            canny_low=config.canny_low_profile_1,
            canny_high=config.canny_high_profile_1,
        )

        edges_2, contour_2, contour_count_2 = self._run_profile(
            image=input_image,
            gray=gray,
            blur_kernel=config.blur_kernel_profile_2,
            canny_low=config.canny_low_profile_2,
            canny_high=config.canny_high_profile_2,
        )

        results: dict[str, np.ndarray] = {
            "01_original": input_image,
            "02_edges_profile_1": edges_1,
            "03_contours_profile_1": contour_1,
            "04_edges_profile_2": edges_2,
            "05_contours_profile_2": contour_2,
        }

        return self._save_results(
            results=results,
            input_path=input_path,
            config=config,
            contour_count_1=contour_count_1,
            contour_count_2=contour_count_2,
        )

    def _run_profile(
        self,
        image: np.ndarray,
        gray: np.ndarray,
        blur_kernel: int,
        canny_low: int,
        canny_high: int,
    ) -> tuple[np.ndarray, np.ndarray, int]:
        if blur_kernel % 2 == 0:
            blur_kernel += 1

        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), sigmaX=0)
        edges = cv2.Canny(blurred, threshold1=canny_low, threshold2=canny_high)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_image = image.copy()
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)

        return edges, contour_image, len(contours)

    def _save_results(
        self,
        results: dict[str, np.ndarray],
        input_path: Path,
        config: EdgeDetectionConfig,
        contour_count_1: int,
        contour_count_2: int,
    ) -> dict[str, Path]:
        output_paths: dict[str, Path] = {}
        config.output_dir.mkdir(parents=True, exist_ok=True)

        for name, image in results.items():
            output_path = config.output_dir / f"{name}.png"
            self._image_io.save(output_path, image)
            output_paths[name] = output_path

            if config.show_windows:
                self._image_io.show(name, image)

        summary_path = config.output_dir / "run_summary_edges.txt"
        summary_path.write_text(
            self._build_summary_text(
                input_path=input_path,
                outputs=output_paths,
                config=config,
                contour_count_1=contour_count_1,
                contour_count_2=contour_count_2,
            ),
            encoding="utf-8",
        )
        output_paths["run_summary_edges"] = summary_path
        return output_paths

    @staticmethod
    def _build_summary_text(
        input_path: Path,
        outputs: dict[str, Path],
        config: EdgeDetectionConfig,
        contour_count_1: int,
        contour_count_2: int,
    ) -> str:
        lines = [
            f"Input image: {input_path}",
            "",
            "Task 1: Edge detection and contour drawing.",
            "Profile 1:",
            f"- Gaussian blur kernel: {config.blur_kernel_profile_1}",
            f"- Canny low/high: {config.canny_low_profile_1}/{config.canny_high_profile_1}",
            f"- Detected contour count: {contour_count_1}",
            "",
            "Profile 2:",
            f"- Gaussian blur kernel: {config.blur_kernel_profile_2}",
            f"- Canny low/high: {config.canny_low_profile_2}/{config.canny_high_profile_2}",
            f"- Detected contour count: {contour_count_2}",
            "",
            "Generated files:",
        ]
        for key, path in outputs.items():
            lines.append(f"- {key}: {path}")
        return "\n".join(lines)
