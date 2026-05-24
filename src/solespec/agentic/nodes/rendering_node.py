from pathlib import Path

from src.solespec.agentic.state import TechPackState
from src.solespec.document_engine.overlay_generator import OverlayGenerator
from src.solespec.document_engine.technical_drawing_generator import (
    TechnicalDrawingGenerator,
)
from src.solespec.rendering_engine.blender_renderer import BlenderRenderer
from src.solespec.utils.scene_export import export_scene_glb


def rendering_node(state: TechPackState) -> TechPackState:
    input_path = Path(state["input_path"])
    output_dir = Path(state.get("output_dir", "outputs"))

    normalized_glb_path = export_scene_glb(
        state["scene"],
        output_dir / "intermediate" / f"{input_path.stem}_normalized.glb",
    )

    renderer = BlenderRenderer()

    renders = renderer.render_views(
        glb_path=normalized_glb_path,
        output_dir=output_dir / "blender_renders",
    )

    annotated_renders = OverlayGenerator().generate_measurement_overlays(
        renders=renders,
        output_dir=output_dir / "annotated",
        measurements=state["measurements"],
    )
    technical_drawings = TechnicalDrawingGenerator().generate_drawings(
        renders=renders,
        output_dir=output_dir / "technical_drawings",
        measurements=state["measurements"],
    )
    annotated_renders.extend(technical_drawings)

    return {
        **state,
        "renders": renders,
        "annotated_renders": annotated_renders,
    }
