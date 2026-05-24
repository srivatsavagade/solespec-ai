from pathlib import Path
import json
import trimesh


def inspect_glb(glb_path: str):
    path = Path(glb_path)

    scene = trimesh.load(path, force="scene")

    print("=" * 60)
    print("SCENE INFO")
    print("=" * 60)

    print(f"Geometry count : {len(scene.geometry)}")
    print(f"Scene bounds   : {scene.bounds}")

    debug = {
        "geometry": [],
        "materials": [],
    }

    print("\n")
    print("=" * 60)
    print("GEOMETRY")
    print("=" * 60)

    for name, mesh in scene.geometry.items():

        print(f"\nMesh Name: {name}")
        print(f"Vertices : {len(mesh.vertices)}")
        print(f"Faces    : {len(mesh.faces)}")
        print(f"Bounds   : {mesh.bounds}")

        material_name = None

        if hasattr(mesh.visual, "material"):
            material = mesh.visual.material

            if material:
                material_name = getattr(material, "name", None)

        print(f"Material : {material_name}")

        debug["geometry"].append({
            "mesh_name": name,
            "vertices": len(mesh.vertices),
            "faces": len(mesh.faces),
            "bounds": mesh.bounds.tolist(),
            "material": material_name,
        })

    print("\n")
    print("=" * 60)
    print("MATERIALS")
    print("=" * 60)

    seen_materials = set()

    for _, mesh in scene.geometry.items():

        if not hasattr(mesh.visual, "material"):
            continue

        material = mesh.visual.material

        if material is None:
            continue

        material_name = getattr(material, "name", "unknown")

        if material_name in seen_materials:
            continue

        seen_materials.add(material_name)

        print(f"\nMaterial: {material_name}")

        base_color = getattr(material, "baseColorFactor", None)

        print(f"Base Color Factor: {base_color}")

        debug["materials"].append({
            "name": material_name,
            "base_color_factor": (
                list(base_color) if base_color is not None else None
            )
        })

    output_json = path.with_suffix(".inspection.json")

    with open(output_json, "w") as f:
        json.dump(debug, f, indent=2)

    print("\n")
    print("=" * 60)
    print(f"Inspection JSON saved to: {output_json}")
    print("=" * 60)


if __name__ == "__main__":
    inspect_glb("input/used_new_balance_574_classic______free.glb")
