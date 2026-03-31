from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.infrastructure.image_io import ImageIO


@dataclass(frozen=True)
class LineDetectionConfig:
    output_dir: Path
    show_windows: bool = False
    blur_kernel: int = 5
    canny_low: int = 50
    canny_high: int = 150
    threshold_profile_1: int = 30
    min_line_length_profile_1: int = 10
    max_line_gap_profile_1: int = 18
    threshold_profile_2: int = 40
    min_line_length_profile_2: int = 28
    max_line_gap_profile_2: int = 10
    min_center_distance_profile_2: float = 32.0
    max_angle_difference_profile_2: float = 8.0
    max_lines_profile_2: int = 30
    object_mask_sat_threshold: int = 25
    contour_min_area: float = 80.0
    contour_circularity_threshold: float = 0.82
    circle_mask_dilate_kernel: int = 5
    hough_circle_dp: float = 1.2
    hough_circle_min_dist: float = 60.0
    hough_circle_param1: float = 120.0
    hough_circle_param2: float = 22.0
    hough_circle_min_radius: int = 18
    hough_circle_max_radius: int = 120
    hough_circle_mask_margin: int = 5
    dedupe_center_distance_profile_1: float = 6.0
    dedupe_angle_difference_profile_1: float = 8.0
    line_draw_thickness: int = 2


class LineDetectionUseCase:
    """Detect line segments and filter short/near-duplicate lines."""

    def __init__(self, image_io: ImageIO) -> None:
        self._image_io = image_io

    def execute(self, input_image: np.ndarray, input_path: Path, config: LineDetectionConfig) -> dict[str, Path]:
        gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
        blur_kernel = config.blur_kernel + 1 if config.blur_kernel % 2 == 0 else config.blur_kernel
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), sigmaX=1.0)
        edges = cv2.Canny(blurred, threshold1=config.canny_low, threshold2=config.canny_high)
        edges = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
            iterations=1,
        )
        line_edges = self._remove_circular_regions_from_edges(
            image=input_image,
            edges=edges,
            sat_threshold=config.object_mask_sat_threshold,
            min_area=config.contour_min_area,
            circularity_threshold=config.contour_circularity_threshold,
            dilate_kernel=config.circle_mask_dilate_kernel,
            hough_dp=config.hough_circle_dp,
            hough_min_dist=config.hough_circle_min_dist,
            hough_param1=config.hough_circle_param1,
            hough_param2=config.hough_circle_param2,
            hough_min_radius=config.hough_circle_min_radius,
            hough_max_radius=config.hough_circle_max_radius,
            hough_mask_margin=config.hough_circle_mask_margin,
        )

        lines_all_hough = self._detect_lines(
            edges=line_edges,
            threshold=config.threshold_profile_1,
            min_line_length=config.min_line_length_profile_1,
            max_line_gap=config.max_line_gap_profile_1,
        )
        lines_all = self._suppress_close_lines(
            lines=lines_all_hough,
            min_center_distance=config.dedupe_center_distance_profile_1,
            max_angle_difference=config.dedupe_angle_difference_profile_1,
            max_lines=600,
        )

        # Stage 2 in assignment: remove too-short segments.
        lines_profile_2_hough = self._detect_lines(
            edges=line_edges,
            threshold=config.threshold_profile_2,
            min_line_length=config.min_line_length_profile_2,
            max_line_gap=config.max_line_gap_profile_2,
        )
        lines_no_short = self._suppress_close_lines(
            lines=lines_profile_2_hough,
            min_center_distance=config.dedupe_center_distance_profile_1,
            max_angle_difference=config.dedupe_angle_difference_profile_1,
            max_lines=600,
        )

        # Stage 3 in assignment: remove lines that are too close to each other.
        lines_no_near = self._suppress_close_lines(
            lines=lines_no_short,
            min_center_distance=config.min_center_distance_profile_2,
            max_angle_difference=config.max_angle_difference_profile_2,
            max_lines=config.max_lines_profile_2,
        )

        short_removed_count = max(0, len(lines_all) - len(lines_no_short))
        near_removed_count = max(0, len(lines_no_short) - len(lines_no_near))

        image_all = self._draw_lines(
            self._prepare_visual_base(input_image),
            lines_all,
            color=(0, 0, 255),
            thickness=config.line_draw_thickness,
        )
        image_no_short = self._draw_lines(
            self._prepare_visual_base(input_image),
            lines_no_short,
            color=(0, 0, 255),
            thickness=config.line_draw_thickness,
        )
        image_no_near = self._draw_lines(
            self._prepare_visual_base(input_image),
            lines_no_near,
            color=(0, 0, 255),
            thickness=config.line_draw_thickness,
        )

        results: dict[str, np.ndarray] = {
            "01_tat_ca_duong_thang": image_all,
            "02_loai_doan_qua_ngan": image_no_short,
            "03_loai_duong_qua_gan": image_no_near,
        }

        return self._save_results(
            results=results,
            input_path=input_path,
            config=config,
            lines_all_count=len(lines_all),
            lines_no_short_count=len(lines_no_short),
            lines_no_near_count=len(lines_no_near),
            short_removed_count=short_removed_count,
            near_removed_count=near_removed_count,
            hough_all_count=len(lines_all_hough),
            hough_profile_2_count=len(lines_profile_2_hough),
        )


    @staticmethod
    def _detect_lines(
        edges: np.ndarray,
        threshold: int,
        min_line_length: int,
        max_line_gap: int,
    ) -> list[np.ndarray]:
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=threshold,
            minLineLength=min_line_length,
            maxLineGap=max_line_gap,
        )

        if lines is None:
            return []

        return [line[0] for line in lines]

    @staticmethod
    def _build_object_mask(image: np.ndarray, sat_threshold: int) -> np.ndarray:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1]
        _, mask_otsu = cv2.threshold(sat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, mask_fixed = cv2.threshold(sat, sat_threshold, 255, cv2.THRESH_BINARY)
        mask = cv2.bitwise_or(mask_otsu, mask_fixed)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        return mask

    @staticmethod
    def _remove_circular_regions_from_edges(
        image: np.ndarray,
        edges: np.ndarray,
        sat_threshold: int,
        min_area: float,
        circularity_threshold: float,
        dilate_kernel: int,
        hough_dp: float,
        hough_min_dist: float,
        hough_param1: float,
        hough_param2: float,
        hough_min_radius: int,
        hough_max_radius: int,
        hough_mask_margin: int,
    ) -> np.ndarray:
        object_mask = LineDetectionUseCase._build_object_mask(image, sat_threshold=sat_threshold)
        contours, _ = cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        circle_mask = np.zeros_like(edges)

        for contour in contours:
            area = float(cv2.contourArea(contour))
            if area < min_area:
                continue

            perimeter = float(cv2.arcLength(contour, True))
            if perimeter <= 0:
                continue

            circularity = (4.0 * np.pi * area) / (perimeter * perimeter)
            if circularity >= circularity_threshold:
                cv2.drawContours(circle_mask, [contour], contourIdx=-1, color=255, thickness=cv2.FILLED)

        # Add Hough-based circle masks to robustly remove circular objects even when touching rectangles.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), sigmaX=1.2)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=hough_dp,
            minDist=hough_min_dist,
            param1=hough_param1,
            param2=hough_param2,
            minRadius=hough_min_radius,
            maxRadius=hough_max_radius,
        )
        if circles is not None:
            for x, y, r in np.round(circles[0]).astype(int):
                rr = int(max(1, r + hough_mask_margin))
                cv2.circle(circle_mask, (int(x), int(y)), rr, color=255, thickness=cv2.FILLED)

        kernel_size = dilate_kernel + 1 if dilate_kernel % 2 == 0 else dilate_kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        circle_mask = cv2.dilate(circle_mask, kernel, iterations=1)

        cleaned_edges = edges.copy()
        cleaned_edges[circle_mask > 0] = 0
        return cleaned_edges

    @staticmethod
    def _suppress_close_lines(
        lines: list[np.ndarray],
        min_center_distance: float,
        max_angle_difference: float,
        max_lines: int,
    ) -> list[np.ndarray]:
        if not lines:
            return []

        lines_sorted = sorted(lines, key=LineDetectionUseCase._line_length, reverse=True)
        kept: list[np.ndarray] = []
        for line in lines_sorted:
            x1, y1, x2, y2 = line
            center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
            angle = LineDetectionUseCase._line_angle_degrees(line)

            is_near_existing = False
            for existing in kept:
                ex1, ey1, ex2, ey2 = existing
                existing_angle = LineDetectionUseCase._line_angle_degrees(existing)
                angle_diff = abs(angle - existing_angle)
                angle_diff = min(angle_diff, 180.0 - angle_diff)

                if angle_diff < max_angle_difference:
                    line_len = float(np.hypot(ex2 - ex1, ey2 - ey1))
                    if line_len > 0:
                        # Orthogonal distance from center of candidate to the infinite line of `existing`
                        distance = abs((ex2 - ex1) * (ey1 - center[1]) - (ex1 - center[0]) * (ey2 - ey1)) / line_len
                    else:
                        distance = float(np.hypot(center[0] - ex1, center[1] - ey1))
                        
                    if distance < min_center_distance:
                        is_near_existing = True
                        break

            if not is_near_existing:
                kept.append(line)
                if len(kept) >= max_lines:
                    break

        return kept

    @staticmethod
    def _line_length(line: np.ndarray) -> float:
        x1, y1, x2, y2 = line
        return float(np.hypot(x2 - x1, y2 - y1))

    @staticmethod
    def _line_angle_degrees(line: np.ndarray) -> float:
        x1, y1, x2, y2 = line
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        return float((angle + 180.0) % 180.0)

    @staticmethod
    def _prepare_visual_base(image: np.ndarray) -> np.ndarray:
        # Keep original colors but darken slightly so white lines stand out like edge maps.
        return cv2.convertScaleAbs(image, alpha=0.52, beta=0)

    @staticmethod
    def _draw_lines(
        image: np.ndarray,
        lines: list[np.ndarray],
        color: tuple[int, int, int],
        thickness: int,
    ) -> np.ndarray:
        for line in lines:
            x1, y1, x2, y2 = line
            cv2.line(image, (x1, y1), (x2, y2), color, thickness, lineType=cv2.LINE_8)
        return image

    def _save_results(
        self,
        results: dict[str, np.ndarray],
        input_path: Path,
        config: LineDetectionConfig,
        lines_all_count: int,
        lines_no_short_count: int,
        lines_no_near_count: int,
        short_removed_count: int,
        near_removed_count: int,
        hough_all_count: int,
        hough_profile_2_count: int,
    ) -> dict[str, Path]:
        output_paths: dict[str, Path] = {}
        config.output_dir.mkdir(parents=True, exist_ok=True)

        for name, image in results.items():
            output_path = config.output_dir / f"{name}.png"
            self._image_io.save(output_path, image)
            output_paths[name] = output_path

            if config.show_windows:
                self._image_io.show(name, image)

        summary_path = config.output_dir / "run_summary_lines.txt"
        summary_path.write_text(
            self._build_summary_text(
                input_path=input_path,
                outputs=output_paths,
                config=config,
                lines_all_count=lines_all_count,
                lines_no_short_count=lines_no_short_count,
                lines_no_near_count=lines_no_near_count,
                short_removed_count=short_removed_count,
                near_removed_count=near_removed_count,
                hough_all_count=hough_all_count,
                hough_profile_2_count=hough_profile_2_count,
            ),
            encoding="utf-8",
        )
        output_paths["run_summary_lines"] = summary_path
        return output_paths

    @staticmethod
    def _build_summary_text(
        input_path: Path,
        outputs: dict[str, Path],
        config: LineDetectionConfig,
        lines_all_count: int,
        lines_no_short_count: int,
        lines_no_near_count: int,
        short_removed_count: int,
        near_removed_count: int,
        hough_all_count: int,
        hough_profile_2_count: int,
    ) -> str:
        lines = [
            f"Input image: {input_path}",
            "",
            "Task 2: Detect all possible lines and then filter short/near lines.",
            "Stage 1 - All lines:",
            f"- Hough threshold: {config.threshold_profile_1}",
            f"- minLineLength: {config.min_line_length_profile_1}",
            f"- maxLineGap: {config.max_line_gap_profile_1}",
            f"- Hough candidate lines: {hough_all_count}",
            f"- Number of lines after dedupe: {lines_all_count}",
            "",
            "Stage 2 - Remove short segments:",
            f"- Hough threshold: {config.threshold_profile_2}",
            f"- minLineLength: {config.min_line_length_profile_2}",
            f"- maxLineGap: {config.max_line_gap_profile_2}",
            f"- Hough candidate lines (profile 2): {hough_profile_2_count}",
            f"- Removed short lines: {short_removed_count}",
            f"- Remaining lines: {lines_no_short_count}",
            "",
            "Stage 3 - Remove near lines:",
            f"- Center-distance suppression: {config.min_center_distance_profile_2}",
            f"- Angle suppression (deg): {config.max_angle_difference_profile_2}",
            f"- Max rendered lines: {config.max_lines_profile_2}",
            f"- Removed near-duplicate lines: {near_removed_count}",
            f"- Remaining lines: {lines_no_near_count}",
            "",
            "Generated files:",
        ]
        for key, path in outputs.items():
            lines.append(f"- {key}: {path}")
        return "\n".join(lines)
