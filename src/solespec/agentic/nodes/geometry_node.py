from src.solespec.agentic.state import TechPackState
from src.solespec.geometry_engine.footwear_measurements import FootwearMeasurementEngine
from src.solespec.geometry_engine.geometry_analyzer import GeometryAnalyzer
from src.solespec.material_engine.material_analyzer import MaterialAnalyzer
from src.solespec.review.overrides import apply_review_overrides, load_review_overrides


def geometry_node(state: TechPackState) -> TechPackState:
    scene = state["scene"]
    geometry_engine = GeometryAnalyzer()

    measurements = FootwearMeasurementEngine().analyze(scene)
    components = geometry_engine.extract_components(scene)
    materials = MaterialAnalyzer().analyze(scene)
    review_overrides = load_review_overrides(state.get("review_overrides_path"))
    components, materials, review_notes = apply_review_overrides(
        components=components,
        materials=materials,
        overrides=review_overrides,
    )

    return {
        **state,
        "measurements": measurements,
        "components": components,
        "materials": materials,
        "review_notes": review_notes,
    }
