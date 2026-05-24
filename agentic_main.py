import argparse
import random
from pathlib import Path

import numpy as np

from src.solespec.agentic.graph import build_graph


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate footwear TechPack using LangGraph orchestration."
    )
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

    random.seed(args.seed)
    np.random.seed(args.seed)

    graph = build_graph()
    final_state = graph.invoke(
        {
            "input_path": str(Path(args.input)),
            "output_dir": str(Path(args.output)),
            "seed": args.seed,
            "review_overrides_path": str(Path(args.review_overrides)) if args.review_overrides else None,
            "orientation_overrides_path": (
                str(Path(args.orientation_overrides)) if args.orientation_overrides else None
            ),
        }
    )

    print("LangGraph TechPack orchestration completed.")
    print(f"Schema: {Path(args.output) / 'schemas' / 'techpack_spec.json'}")

    for pdf_path in final_state.get("pdf_paths", []):
        print(f"PDF: {pdf_path}")


if __name__ == "__main__":
    main()
