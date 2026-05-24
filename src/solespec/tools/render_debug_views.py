import trimesh
import copy


INPUT_GLB = "input/used_new_balance_574_classic______free.glb"


def load_scene(glb_path):
    print("Loading GLB...")

    scene = trimesh.load(glb_path, force='scene')

    return scene


def print_scene_info(scene):
    print("\n============================================================")
    print("SCENE INFO")
    print("============================================================")

    print(f"Geometry count : {len(scene.geometry)}")
    print(f"Scene bounds   : {scene.bounds}")

    print("\n============================================================")
    print("GEOMETRY")
    print("============================================================")

    for name, geom in scene.geometry.items():
        print(f"\nMesh Name: {name}")
        print(f"Vertices : {len(geom.vertices)}")
        print(f"Faces    : {len(geom.faces)}")
        print(f"Bounds   : {geom.bounds}")


def render_view(scene):
    print("Opening viewer...")

    # IMPORTANT:
    # Use a COPY so original materials/textures stay intact
    viewer_scene = copy.deepcopy(scene)

    viewer_scene.show()


def main():
    scene = load_scene(INPUT_GLB)

    print_scene_info(scene)

    render_view(scene)

    print("\nDone.")


if __name__ == "__main__":
    main()
