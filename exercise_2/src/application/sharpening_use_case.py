from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.infrastructure.image_io import ImageIO
from src.infrastructure.workspace_image_provider import WorkspaceImageProvider


@dataclass(frozen=True)
class SharpeningConfig:
    input_path: Path | None
    search_root: Path
    output_dir: Path
    show_windows: bool = False
    blur_kernel_size: int = 5
    blur_sigma: float = 0.0
    canny_low_threshold: int = 50
    canny_high_threshold: int = 150


class SharpeningUseCase:
    """Demonstrate Canny-based edge mask filtering for Question 2."""

    def __init__(self, image_io: ImageIO, image_provider: WorkspaceImageProvider) -> None:
        self._image_io = image_io
        self._image_provider = image_provider

    def execute(self, config: SharpeningConfig) -> dict[str, Path]:
        selected_input = self._resolve_input_path(config)
        original_image = self._image_io.load(selected_input)
        gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

        blur_kernel = (config.blur_kernel_size, config.blur_kernel_size)
        blurred_image = cv2.GaussianBlur(original_image, blur_kernel, sigmaX=config.blur_sigma)
        edges_mask = cv2.Canny(
            gray_image,
            threshold1=config.canny_low_threshold,
            threshold2=config.canny_high_threshold,
        )

        edges_mask_3ch = cv2.cvtColor(edges_mask, cv2.COLOR_GRAY2BGR)
        edge_preserved_result = np.where(edges_mask_3ch == 255, original_image, blurred_image)
        edge_preserved_result = edge_preserved_result.astype(np.uint8)

        panel_image = np.hstack([original_image, blurred_image, edge_preserved_result])

        results: dict[str, np.ndarray] = {
            "01_original": original_image,
            "02_blurred": blurred_image,
            "03_canny_mask": edges_mask,
            "04_edge_preserved_result": edge_preserved_result,
            "05_comparison_panel": panel_image,
        }

        output_paths: dict[str, Path] = {}
        config.output_dir.mkdir(parents=True, exist_ok=True)

        for name, image in results.items():
            output_path = config.output_dir / f"{name}.png"
            self._image_io.save(output_path, image)
            output_paths[name] = output_path

            if config.show_windows:
                self._image_io.show(name, image)

        summary_path = config.output_dir / "run_summary_question2.txt"
        summary_path.write_text(
            self._build_summary_text(selected_input=selected_input, outputs=output_paths, config=config),
            encoding="utf-8",
        )
        output_paths["run_summary_question2"] = summary_path

        if config.show_windows:
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return output_paths

    def _resolve_input_path(self, config: SharpeningConfig) -> Path:
        if config.input_path is not None:
            return config.input_path

        images = self._image_provider.list_images(config.search_root)
        return self._image_provider.pick_random(images)

    @staticmethod
    def _build_summary_text(
        selected_input: Path,
        outputs: dict[str, Path],
        config: SharpeningConfig,
    ) -> str:
        lines = [
            f"Anh dau vao duoc chon: {selected_input}",
            "",
            "Phuong phap duoc chon: Canny Edge Detection + Masking",
            "- Buoc 1: Tao mat na bien bang Canny tren anh xam.",
            "- Buoc 2: Tao anh mo toan cuc bang Gaussian Blur.",
            "- Buoc 3: Neu la bien thi giu pixel anh goc, nguoc lai lay pixel anh mo.",
            f"- Tham so Canny: low={config.canny_low_threshold}, high={config.canny_high_threshold}",
            f"- Tham so Gaussian: kernel={config.blur_kernel_size}x{config.blur_kernel_size}, sigma={config.blur_sigma}",
            "",
            "Cac file ket qua:",
        ]

        for key, path in outputs.items():
            lines.append(f"- {key}: {path}")

        return "\n".join(lines)
