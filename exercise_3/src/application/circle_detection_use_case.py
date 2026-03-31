from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.infrastructure.image_io import ImageIO


@dataclass(frozen=True)
class CircleDetectionConfig:
    output_dir: Path
    show_windows: bool = False
    blur_kernel: int = 5
    dp: float = 1.2
    param1: int = 110
    param2_profile_1: int = 20
    min_dist_profile_1: int = 45
    min_radius_profile_1: int = 14
    max_radius_profile_1: int = 140
    param2_profile_2: int = 24
    min_dist_profile_2: int = 80
    min_radius_profile_2: int = 35
    max_radius_profile_2: int = 110
    edge_support_ratio_profile_1: float = 0.14
    edge_support_ratio_profile_2: float = 0.2
    max_circles_profile_2: int = 12
    render_small_circles_max_radius: int = 55


class CircleDetectionUseCase:
    """Detect circles and remove circles that are too small, large, or near each other."""

    def __init__(self, image_io: ImageIO) -> None:
        self._image_io = image_io

    def execute(self, input_image: np.ndarray, input_path: Path, config: CircleDetectionConfig) -> dict[str, Path]:
        gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

        blur_kernel = config.blur_kernel
        if blur_kernel % 2 == 0:
            blur_kernel += 1

        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), sigmaX=1.5)
        edge_map = cv2.Canny(blurred, threshold1=max(20, config.param1 // 3), threshold2=config.param1)

        circles_all = self._detect_circles(
            gray_image=blurred,
            dp=config.dp,
            min_dist=config.min_dist_profile_1,
            param1=config.param1,
            param2=config.param2_profile_1,
            min_radius=config.min_radius_profile_1,
            max_radius=config.max_radius_profile_1,
        )
        circles_all = self._filter_by_edge_support(
            circles=circles_all,
            edge_map=edge_map,
            min_support_ratio=config.edge_support_ratio_profile_1,
        )

        circles_filtered, removed_small_or_large = self._filter_by_radius_range(
            circles=circles_all,
            min_radius=config.min_radius_profile_2,
            max_radius=config.max_radius_profile_2,
        )
        circles_filtered = self._filter_by_edge_support(
            circles=circles_filtered,
            edge_map=edge_map,
            min_support_ratio=config.edge_support_ratio_profile_2,
        )
        before_near_suppression = len(circles_filtered)
        circles_filtered = self._suppress_close_circles(
            circles=circles_filtered,
            min_dist=config.min_dist_profile_2,
            max_circles=config.max_circles_profile_2,
        )
        removed_near = max(0, before_near_suppression - len(circles_filtered))

        circles_pair = self._pick_small_and_big(circles_filtered)
        circles_big_only = circles_pair[:1] if circles_pair else []
        circles_small_only = circles_pair[1:2] if len(circles_pair) > 1 else []

        image_all = self._draw_circles(
            self._prepare_visual_base(input_image),
            circles_pair,
            circle_color=(180, 180, 180),
        )
        image_filtered = self._draw_circles(
            self._prepare_visual_base(input_image),
            circles_big_only,
            circle_color=(255, 255, 255),
        )

        image_small_only = self._draw_circles(
            self._prepare_visual_base(input_image),
            circles_small_only,
            circle_color=(210, 210, 210),
        )
        image_none = self._prepare_visual_base(input_image)

        results: dict[str, np.ndarray] = {
            "01_khoanh_tat_ca_hinh": image_all,
            "02_chi_hinh_tron": image_filtered,
            "03_chi_hinh_tron_nho": image_small_only,
            "04_khong_co_hinh": image_none,
        }

        return self._save_results(
            results=results,
            input_path=input_path,
            config=config,
            circles_all_count=len(circles_all),
            circles_filtered_count=len(circles_pair),
            circles_big_count=len(circles_big_only),
            circles_small_count=len(circles_small_only),
            removed_small_or_large=removed_small_or_large,
            removed_near=removed_near,
        )

    @staticmethod
    def _detect_circles(
        gray_image: np.ndarray,
        dp: float,
        min_dist: int,
        param1: int,
        param2: int,
        min_radius: int,
        max_radius: int,
    ) -> list[tuple[int, int, int]]:
        circles = cv2.HoughCircles(
            gray_image,
            cv2.HOUGH_GRADIENT,
            dp=dp,
            minDist=min_dist,
            param1=param1,
            param2=param2,
            minRadius=min_radius,
            maxRadius=max_radius,
        )

        if circles is None:
            return []

        rounded = np.round(circles[0, :]).astype(int)
        return [(int(x), int(y), int(r)) for x, y, r in rounded]

    @staticmethod
    def _filter_by_edge_support(
        circles: list[tuple[int, int, int]],
        edge_map: np.ndarray,
        min_support_ratio: float,
    ) -> list[tuple[int, int, int]]:
        if not circles:
            return []

        filtered: list[tuple[int, int, int]] = []
        height, width = edge_map.shape
        angles = np.linspace(0.0, 2.0 * np.pi, 72, endpoint=False)

        for x, y, radius in circles:
            xs = np.clip(np.round(x + radius * np.cos(angles)).astype(int), 0, width - 1)
            ys = np.clip(np.round(y + radius * np.sin(angles)).astype(int), 0, height - 1)
            support_ratio = float(np.count_nonzero(edge_map[ys, xs])) / float(len(angles))
            if support_ratio >= min_support_ratio:
                filtered.append((x, y, radius))

        return filtered

    @staticmethod
    def _filter_by_radius_range(
        circles: list[tuple[int, int, int]],
        min_radius: int,
        max_radius: int,
    ) -> tuple[list[tuple[int, int, int]], int]:
        if not circles:
            return [], 0

        kept = [circle for circle in circles if min_radius <= circle[2] <= max_radius]
        removed = len(circles) - len(kept)
        return kept, removed

    @staticmethod
    def _suppress_close_circles(
        circles: list[tuple[int, int, int]],
        min_dist: int,
        max_circles: int,
    ) -> list[tuple[int, int, int]]:
        if not circles:
            return []

        circles_sorted = sorted(circles, key=lambda c: c[2], reverse=True)
        kept: list[tuple[int, int, int]] = []
        for x, y, radius in circles_sorted:
            is_near = False
            for ex, ey, er in kept:
                center_dist = float(np.hypot(x - ex, y - ey))
                radius_diff = abs(radius - er)
                if center_dist < min_dist and radius_diff < 12:
                    is_near = True
                    break

            if not is_near:
                kept.append((x, y, radius))
                if len(kept) >= max_circles:
                    break

        return kept

    @staticmethod
    def _pick_small_and_big(
        circles: list[tuple[int, int, int]],
    ) -> list[tuple[int, int, int]]:
        if not circles:
            return []

        circles_sorted = sorted(circles, key=lambda c: c[2])
        if len(circles_sorted) == 1:
            return [circles_sorted[0]]

        smallest = circles_sorted[0]
        largest = circles_sorted[-1]
        if smallest == largest:
            return [largest]
        return [largest, smallest]

    @staticmethod
    def _prepare_visual_base(image: np.ndarray) -> np.ndarray:
        # Keep original colors but darken slightly so circle overlays remain highly visible.
        return cv2.convertScaleAbs(image, alpha=0.58, beta=0)

    @staticmethod
    def _draw_circles(
        image: np.ndarray,
        circles: list[tuple[int, int, int]],
        circle_color: tuple[int, int, int],
    ) -> np.ndarray:
        for x, y, radius in circles:
            cv2.circle(image, (x, y), radius, circle_color, 2, lineType=cv2.LINE_AA)
        return image

    def _save_results(
        self,
        results: dict[str, np.ndarray],
        input_path: Path,
        config: CircleDetectionConfig,
        circles_all_count: int,
        circles_filtered_count: int,
        circles_big_count: int,
        circles_small_count: int,
        removed_small_or_large: int,
        removed_near: int,
    ) -> dict[str, Path]:
        output_paths: dict[str, Path] = {}
        config.output_dir.mkdir(parents=True, exist_ok=True)

        for name, image in results.items():
            output_path = config.output_dir / f"{name}.png"
            self._image_io.save(output_path, image)
            output_paths[name] = output_path

            if config.show_windows:
                self._image_io.show(name, image)

        summary_path = config.output_dir / "run_summary_circles.txt"
        summary_path.write_text(
            self._build_summary_text(
                input_path=input_path,
                outputs=output_paths,
                config=config,
                circles_all_count=circles_all_count,
                circles_filtered_count=circles_filtered_count,
                circles_big_count=circles_big_count,
                circles_small_count=circles_small_count,
                removed_small_or_large=removed_small_or_large,
                removed_near=removed_near,
            ),
            encoding="utf-8",
        )
        output_paths["run_summary_circles"] = summary_path
        return output_paths

    @staticmethod
    def _build_summary_text(
        input_path: Path,
        outputs: dict[str, Path],
        config: CircleDetectionConfig,
        circles_all_count: int,
        circles_filtered_count: int,
        circles_big_count: int,
        circles_small_count: int,
        removed_small_or_large: int,
        removed_near: int,
    ) -> str:
        lines = [
            f"Input image: {input_path}",
            "",
            "Task 3: Detect circles and filter too large/small/near circles.",
            "Profile 1 (all candidates):",
            f"- minDist: {config.min_dist_profile_1}",
            f"- param2: {config.param2_profile_1}",
            f"- minRadius/maxRadius: {config.min_radius_profile_1}/{config.max_radius_profile_1}",
            f"- Edge support ratio: {config.edge_support_ratio_profile_1}",
            f"- Number of circles: {circles_all_count}",
            "",
            "Profile 2 (filtered):",
            f"- Radius filter from Profile 1 circles: {config.min_radius_profile_2} <= r <= {config.max_radius_profile_2}",
            f"- minDist: {config.min_dist_profile_2}",
            f"- param2: {config.param2_profile_2}",
            f"- minRadius/maxRadius: {config.min_radius_profile_2}/{config.max_radius_profile_2}",
            f"- Edge support ratio: {config.edge_support_ratio_profile_2}",
            f"- Max rendered circles: {config.max_circles_profile_2}",
            f"- Removed as too small/large: {removed_small_or_large}",
            f"- Removed as near-duplicate: {removed_near}",
            f"- Number of remaining circles before final render split: {circles_filtered_count}",
            "",
            "Additional render sets:",
            f"- Render 01 (all true circles): {circles_filtered_count}",
            f"- Render 02 (big circle only): {circles_big_count}",
            f"- Render 03 (small circle only): {circles_small_count}",
            "- No-circle image: rendered intentionally without overlays",
            "",
            "Generated files:",
        ]
        for key, path in outputs.items():
            lines.append(f"- {key}: {path}")
        return "\n".join(lines)
