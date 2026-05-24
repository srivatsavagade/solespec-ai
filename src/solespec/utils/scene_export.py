from pathlib import Path

import trimesh


def export_scene_glb(scene: trimesh.Scene, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.export(output_path)

    if not output_path.exists():
        raise FileNotFoundError(f"Failed to export normalized GLB: {output_path}")

    return output_path
