from pathlib import Path

from src.solespec.agentic.state import TechPackState
from src.solespec.normalization.orientation_overrides import (
    apply_orientation_overrides,
    load_orientation_overrides,
)
from src.solespec.normalization.scale_normalizer import ScaleNormalizer
from src.solespec.normalization.scene_normalizer import SceneNormalizer


def normalization_node(state: TechPackState) -> TechPackState:
    input_path = Path(state["input_path"])
    orientation_overrides_path = state.get("orientation_overrides_path")

    scene = SceneNormalizer().normalize(state["scene"])
    orientation_overrides = load_orientation_overrides(
        Path(orientation_overrides_path) if orientation_overrides_path else None
    )
    scene, orientation_metadata = apply_orientation_overrides(
        scene=scene,
        input_path=input_path,
        overrides=orientation_overrides,
    )
    scene, scale_metadata = ScaleNormalizer(target_length_mm=280.0).normalize(scene)
    scale_metadata["orientation_override"] = orientation_metadata

    return {
        **state,
        "scene": scene,
        "scale_metadata": scale_metadata,
    }
