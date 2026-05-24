from datetime import datetime, timezone
from pathlib import Path
import platform
import sys

from src.solespec.schemas.techpack_schema import TechPackSpec


def build_run_manifest(
    spec: TechPackSpec,
    input_path: Path,
    output_dir: Path,
    seed: int,
) -> dict:
    outputs = [
        str(output_dir / "schemas" / "techpack_spec.json"),
        str(output_dir / "techpacks" / "cover_sheet.pdf"),
        str(output_dir / "techpacks" / "measurement_sheet.pdf"),
        str(output_dir / "techpacks" / "technical_drawing_sheet.pdf"),
        str(output_dir / "techpacks" / "bom_colorway_sheet.pdf"),
        str(output_dir / "techpacks" / "validation_report.pdf"),
    ]

    return {
        "run_completed_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path),
        "output_dir": str(output_dir),
        "seed": seed,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "selected_capabilities": [
            "multi_view_rendering",
            "geometry_measurement",
            "material_colorway_extraction",
            "technical_2d_drawings",
            "retrieval_grounded_manufacturing_review",
            "validation_confidence_scoring",
        ],
        "normalization": spec.normalization_metadata,
        "confidence_scores": (
            spec.confidence_scores.__dict__
            if spec.confidence_scores is not None
            else None
        ),
        "outputs": outputs,
        "validation_issue_count": len(spec.validation_issues),
    }
