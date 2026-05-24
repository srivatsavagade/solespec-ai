from pathlib import Path

from src.solespec.agentic.state import TechPackState
from src.solespec.document_engine.pdf_composer import PDFComposer
from src.solespec.utils.json_io import save_json
from src.solespec.utils.run_manifest import build_run_manifest


def pdf_node(state: TechPackState) -> TechPackState:
    output_dir = Path(state.get("output_dir", "outputs"))
    input_path = Path(state["input_path"])
    spec = state["spec"]

    spec.run_manifest = build_run_manifest(
        spec=spec,
        input_path=input_path,
        output_dir=output_dir,
        seed=int(state.get("seed", 42)),
    )

    save_json(spec.to_dict(), output_dir / "schemas" / "techpack_spec.json")
    save_json(spec.run_manifest, output_dir / "schemas" / "run_manifest.json")

    pdf_composer = PDFComposer()
    pdf_paths = [
        output_dir / "techpacks" / "cover_sheet.pdf",
        output_dir / "techpacks" / "measurement_sheet.pdf",
        output_dir / "techpacks" / "technical_drawing_sheet.pdf",
        output_dir / "techpacks" / "bom_colorway_sheet.pdf",
        output_dir / "techpacks" / "validation_report.pdf",
    ]

    pdf_composer.compose_cover_sheet(spec, pdf_paths[0])
    pdf_composer.compose_measurement_sheet(spec, pdf_paths[1])
    pdf_composer.compose_technical_drawing_sheet(spec, pdf_paths[2])
    pdf_composer.compose_bom_colorway_sheet(spec, pdf_paths[3])
    pdf_composer.compose_validation_report(spec, pdf_paths[4])

    return {
        **state,
        "pdf_paths": [str(path) for path in pdf_paths],
    }
