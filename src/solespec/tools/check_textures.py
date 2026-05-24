import trimesh


scene = trimesh.load("input/used_new_balance_574_classic______free.glb", force="scene")

print("\nTEXTURE INSPECTION")
print("=" * 60)

for name, mesh in scene.geometry.items():

    print(f"\nMesh: {name}")

    visual = mesh.visual

    print("Visual Type:", type(visual))

    if hasattr(visual, "uv") and visual.uv is not None:
        print("UV coordinates: PRESENT")
    else:
        print("UV coordinates: MISSING")

    if hasattr(visual, "material"):

        material = visual.material

        print("Material:", material)

        base_texture = getattr(material, "baseColorTexture", None)

        if base_texture is not None:
            print("Base Color Texture: PRESENT")
        else:
            print("Base Color Texture: MISSING")

        image = getattr(material, "image", None)

        if image is not None:
            print("Embedded Image Texture: PRESENT")
            print("Image Size:", image.size)
        else:
            print("Embedded Image Texture: MISSING")
