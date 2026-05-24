from pathlib import Path
import trimesh


OUTPUT_DIR = Path("outputs/native_renders")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading GLB...")

scene = trimesh.load(
    "input/used_new_balance_574_classic______free.glb",
    force="scene"
)

print("Saving render...")

png = scene.save_image(
    resolution=(1400, 1000),
    visible=True
)

output_path = OUTPUT_DIR / "native_render.png"

with open(output_path, "wb") as f:
    f.write(png)

print(f"Saved: {output_path}")
