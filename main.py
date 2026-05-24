import argparse
from pathlib import Path

from src.solespec.pipelines.techpack_pipeline import TechPackPipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Generate footwear TechPack from GLB model.")
    parser.add_argument("--input", required=True, help="Path to input .glb file")
    parser.add_argument("--output", default="outputs", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Reproducibility seed")
    parser.add_argument(
        "--review-overrides",
        help="Optional JSON file with human-reviewed component/material overrides",
    )
    parser.add_argument(
        "--orientation-overrides",
        help="Optional JSON file with asset-specific orientation corrections",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    pipeline = TechPackPipeline(
        input_path=Path(args.input),
        output_dir=Path(args.output),
        seed=args.seed,
        review_overrides_path=Path(args.review_overrides) if args.review_overrides else None,
        orientation_overrides_path=(
            Path(args.orientation_overrides) if args.orientation_overrides else None
        ),
    )

    pipeline.run()


if __name__ == "__main__":
    main()
