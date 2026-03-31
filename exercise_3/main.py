from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from src.application.circle_detection_use_case import CircleDetectionConfig, CircleDetectionUseCase
from src.application.edge_detection_use_case import EdgeDetectionConfig, EdgeDetectionUseCase
from src.application.line_detection_use_case import LineDetectionConfig, LineDetectionUseCase
from src.infrastructure.image_io import ImageIO
from src.infrastructure.workspace_image_provider import WorkspaceImageProvider


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Exercise 3: edge contour, line detection, and circle detection"
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
        default=project_root / "outputs",
        help="Directory where output folders are saved.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible image selection.",
    )
    parser.add_argument(
        "--no-show",
        dest="show",
        action="store_false",
        help="Disable image display windows.",
    )
    parser.set_defaults(show=True)
    return parser.parse_args()


def resolve_input_path(args: argparse.Namespace, provider: WorkspaceImageProvider) -> Path:
    if args.input is not None:
        return args.input

    images = provider.list_images(args.search_root)
    return provider.pick_random(images)


def main() -> None:
    args = parse_args()

    image_io = ImageIO()
    image_provider = WorkspaceImageProvider(seed=args.seed)
    input_path = resolve_input_path(args, image_provider)
    original_image = image_io.load(input_path)

    edge_use_case = EdgeDetectionUseCase(image_io=image_io)
    line_use_case = LineDetectionUseCase(image_io=image_io)
    circle_use_case = CircleDetectionUseCase(image_io=image_io)

    edge_outputs = edge_use_case.execute(
        input_image=original_image,
        input_path=input_path,
        config=EdgeDetectionConfig(
            output_dir=args.output_dir / "edge",
            show_windows=args.show,
        ),
    )

    line_outputs = line_use_case.execute(
        input_image=original_image,
        input_path=input_path,
        config=LineDetectionConfig(
            output_dir=args.output_dir / "lines",
            show_windows=args.show,
        ),
    )

    circle_outputs = circle_use_case.execute(
        input_image=original_image,
        input_path=input_path,
        config=CircleDetectionConfig(
            output_dir=args.output_dir / "circles",
            show_windows=args.show,
        ),
    )

    print("Exercise 3 pipeline completed.")
    print(f"Input image: {input_path}")

    print("\n[Edge Detection Outputs]")
    for name, path in edge_outputs.items():
        print(f"- {name}: {path}")

    print("\n[Line Detection Outputs]")
    for name, path in line_outputs.items():
        print(f"- {name}: {path}")

    print("\n[Circle Detection Outputs]")
    for name, path in circle_outputs.items():
        print(f"- {name}: {path}")

    if args.show:
        print("\nPress any key in an image window to close all windows.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
