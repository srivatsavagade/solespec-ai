from pathlib import Path
import trimesh


class GLBLoader:
    def load(self, input_path: Path) -> trimesh.Scene:
        if not input_path.exists():
            raise FileNotFoundError(f"Input GLB not found: {input_path}")

        if input_path.suffix.lower() != ".glb":
            raise ValueError("Only .glb files are supported in this MVP.")

        scene = trimesh.load(input_path, force="scene")

        if not isinstance(scene, trimesh.Scene):
            raise ValueError("Failed to load GLB as trimesh.Scene")

        if len(scene.geometry) == 0:
            raise ValueError("GLB contains no geometry.")

        return scene
