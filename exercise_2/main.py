from __future__ import annotations

import argparse
from pathlib import Path

from src.application.spatial_smoothing_use_case import ExecutionConfig, SpatialSmoothingUseCase
from src.infrastructure.image_io import ImageIO
from src.infrastructure.opencv_filter_engine import OpenCVFilterEngine
from src.infrastructure.workspace_image_provider import WorkspaceImageProvider


def parse_args() -> argparse.Namespace:
    default_search_root = Path(__file__).resolve().parent / "assets"
    parser = argparse.ArgumentParser(
        description="Spatial smoothing filtering assignment pipeline"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional image path. If omitted, a random image from --search-root is used.",
    )
    parser.add_argument(
        "--search-root",
        type=Path,
        default=default_search_root,
        help="Folder used to discover images for random input selection.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs",
        help="Directory where processed images will be saved.",
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
        help="Disable image display windows (useful on headless environments).",
    )
    parser.set_defaults(show=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    use_case = SpatialSmoothingUseCase(
        filter_engine=OpenCVFilterEngine(),
        image_io=ImageIO(),
        image_provider=WorkspaceImageProvider(seed=args.seed),
    )

    outputs = use_case.execute(
        ExecutionConfig(
            input_path=args.input,
            search_root=args.search_root,
            output_dir=args.output_dir,
            show_windows=args.show,
        )
    )

    print("Spatial smoothing pipeline completed.")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
