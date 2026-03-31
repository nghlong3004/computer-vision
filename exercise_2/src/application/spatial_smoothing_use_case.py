from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.domain.contracts import FilterEngine
from src.domain.kernels import KernelFactory
from src.infrastructure.image_io import ImageIO
from src.infrastructure.workspace_image_provider import WorkspaceImageProvider


@dataclass(frozen=True)
class ExecutionConfig:
    input_path: Path | None
    search_root: Path
    output_dir: Path
    show_windows: bool = False


class SpatialSmoothingUseCase:
    """Execute all assignment-required smoothing operations."""

    def __init__(
        self,
        filter_engine: FilterEngine,
        image_io: ImageIO,
        image_provider: WorkspaceImageProvider,
    ) -> None:
        self._filter_engine = filter_engine
        self._image_io = image_io
        self._image_provider = image_provider

    def execute(self, config: ExecutionConfig) -> dict[str, Path]:
        selected_input = self._resolve_input_path(config)
        source_image = self._image_io.load(selected_input)

        mean_1d_horizontal = KernelFactory.mean_1d_horizontal()
        weighted_1d_horizontal = KernelFactory.weighted_1d_horizontal()

        mean_1d_vertical = mean_1d_horizontal.vertical(name="1d_mean_5x1_vertical")
        weighted_1d_vertical = weighted_1d_horizontal.vertical(name="1d_weighted_5x1_vertical")

        mean_2d = KernelFactory.mean_2d()
        weighted_2d = KernelFactory.weighted_2d()

        results: dict[str, np.ndarray] = {
            "01_original_color": source_image,
            "02_1d_mean_1x5_horizontal": self._filter_engine.apply(
                source_image, mean_1d_horizontal.matrix
            ),
            "03_1d_weighted_1x5_horizontal": self._filter_engine.apply(
                source_image, weighted_1d_horizontal.matrix
            ),
            "04_1d_mean_5x1_vertical": self._filter_engine.apply(
                source_image, mean_1d_vertical.matrix
            ),
            "05_1d_weighted_5x1_vertical": self._filter_engine.apply(
                source_image, weighted_1d_vertical.matrix
            ),
            "06_2d_mean_3x3": self._filter_engine.apply(source_image, mean_2d.matrix),
            "07_2d_weighted_3x3": self._filter_engine.apply(source_image, weighted_2d.matrix),
        }

        output_paths: dict[str, Path] = {}
        config.output_dir.mkdir(parents=True, exist_ok=True)

        for name, image in results.items():
            output_path = config.output_dir / f"{name}.png"
            self._image_io.save(output_path, image)
            output_paths[name] = output_path

            if config.show_windows:
                self._image_io.show(name, image)

        summary_path = config.output_dir / "run_summary.txt"
        summary_path.write_text(
            self._build_summary_text(selected_input=selected_input, outputs=output_paths),
            encoding="utf-8",
        )
        output_paths["run_summary"] = summary_path

        if config.show_windows:
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return output_paths

    def _resolve_input_path(self, config: ExecutionConfig) -> Path:
        if config.input_path is not None:
            return config.input_path

        images = self._image_provider.list_images(config.search_root)
        return self._image_provider.pick_random(images)

    @staticmethod
    def _build_summary_text(selected_input: Path, outputs: dict[str, Path]) -> str:
        lines = [
            f"Ảnh đầu vào được chọn: {selected_input}",
            "",
            "Các file kết quả:",
        ]
        for key, path in outputs.items():
            lines.append(f"- {key}: {path}")

        lines.extend(
            [
                "",
                "Ma trận lọc đã dùng:",
                "- 1D trung bình (ngang): [1/5, 1/5, 1/5, 1/5, 1/5]",
                "- 1D có trọng số (ngang): [1, 2, 4, 2, 1] / 10",
                "- 1D trung bình (dọc): chuyển vị từ ma trận lọc ngang",
                "- 1D có trọng số (dọc): chuyển vị từ ma trận lọc ngang",
                "- 2D trung bình 3x3: ones(3x3) / 9",
                "- 2D có trọng số 3x3: [[1,2,1],[2,8,2],[1,2,1]] / 20",
            ]
        )

        return "\n".join(lines)
