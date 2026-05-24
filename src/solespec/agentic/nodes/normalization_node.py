from src.solespec.agentic.state import TechPackState
from src.solespec.normalization.scale_normalizer import ScaleNormalizer
from src.solespec.normalization.scene_normalizer import SceneNormalizer


def normalization_node(state: TechPackState) -> TechPackState:
    scene = SceneNormalizer().normalize(state["scene"])
    scene, scale_metadata = ScaleNormalizer(target_length_mm=280.0).normalize(scene)

    return {
        **state,
        "scene": scene,
        "scale_metadata": scale_metadata,
    }
