from pathlib import Path

from src.solespec.agentic.state import TechPackState
from src.solespec.ingestion.glb_loader import GLBLoader


def ingestion_node(state: TechPackState) -> TechPackState:
    input_path = Path(state["input_path"])

    scene = GLBLoader().load(input_path)

    return {
        **state,
        "scene": scene,
    }
