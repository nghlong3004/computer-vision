from __future__ import annotations

import argparse
from pathlib import Path

from src.application.sharpening_use_case import SharpeningConfig, SharpeningUseCase
from src.infrastructure.image_io import ImageIO
from src.infrastructure.workspace_image_provider import WorkspaceImageProvider


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Question 2: Canny edge mask and edge-preserving result"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional image path. If omitted, a random image in assets/ is used.",
    )
    parser.add_argument(
        "--search-root",
        type=Path,
        default=project_root / "assets",
        help="Folder used to discover images for random selection.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "outputs_question2",
        help="Directory where Question 2 outputs are saved.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible random image selection.",
    )
    parser.add_argument(
        "--no-show",
        dest="show",
        action="store_false",
        help="Disable image display windows.",
    )
    parser.add_argument(
        "--blur-kernel",
        type=int,
        default=5,
        help="Gaussian blur kernel size (odd number).",
    )
    parser.add_argument(
        "--blur-sigma",
        type=float,
        default=0.0,
        help="Gaussian blur sigma.",
    )
    parser.add_argument(
        "--canny-low",
        type=int,
        default=50,
        help="Low threshold for Canny edge detection.",
    )
    parser.add_argument(
        "--canny-high",
        type=int,
        default=150,
        help="High threshold for Canny edge detection.",
    )
    parser.set_defaults(show=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    use_case = SharpeningUseCase(
        image_io=ImageIO(),
        image_provider=WorkspaceImageProvider(seed=args.seed),
    )

    outputs = use_case.execute(
        SharpeningConfig(
            input_path=args.input,
            search_root=args.search_root,
            output_dir=args.output_dir,
            show_windows=args.show,
            blur_kernel_size=args.blur_kernel,
            blur_sigma=args.blur_sigma,
            canny_low_threshold=args.canny_low,
            canny_high_threshold=args.canny_high,
        )
    )

    print("Câu 2 hoàn thành.")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
