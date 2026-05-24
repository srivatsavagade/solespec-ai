import bpy
from pathlib import Path
from math import radians
from mathutils import Vector


PROJECT_ROOT = Path.cwd()

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "blender_renders"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GLB_PATH = str(PROJECT_ROOT / "input" / "used_new_balance_574_classic______free.glb")


# ---------------------------------------------------------
# Cleanup default scene
# ---------------------------------------------------------

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()


# ---------------------------------------------------------
# Import GLB
# ---------------------------------------------------------

bpy.ops.import_scene.gltf(filepath=GLB_PATH)


# ---------------------------------------------------------
# Collect imported meshes
# ---------------------------------------------------------

objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

if not objs:
    raise Exception("No mesh objects imported")


# ---------------------------------------------------------
# Compute scene bounds
# ---------------------------------------------------------

min_corner = [float("inf")] * 3
max_corner = [float("-inf")] * 3

for obj in objs:

    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    for v in bbox:
        for i in range(3):
            min_corner[i] = min(min_corner[i], v[i])
            max_corner[i] = max(max_corner[i], v[i])


size = [
    max_corner[i] - min_corner[i]
    for i in range(3)
]

max_dim = max(size)

center = [
    (min_corner[i] + max_corner[i]) / 2
    for i in range(3)
]


# ---------------------------------------------------------
# Center meshes around origin
# ---------------------------------------------------------

for obj in objs:
    obj.location.x -= center[0]
    obj.location.y -= center[1]
    obj.location.z -= center[2]


# ---------------------------------------------------------
# Camera setup
# ---------------------------------------------------------

cam_data = bpy.data.cameras.new(name="Camera")
cam = bpy.data.objects.new("Camera", cam_data)

bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam

cam.data.type = 'ORTHO'
cam.data.ortho_scale = max_dim * 1.5


# ---------------------------------------------------------
# Lighting
# ---------------------------------------------------------

light_data = bpy.data.lights.new(name="Sun", type='SUN')
light = bpy.data.objects.new(name="Sun", object_data=light_data)

bpy.context.collection.objects.link(light)

light.location = (5, -5, 10)

light.data.energy = 5


# ---------------------------------------------------------
# Render settings
# ---------------------------------------------------------

scene = bpy.context.scene

scene.render.engine = 'CYCLES'

scene.cycles.samples = 64

scene.render.resolution_x = 1400
scene.render.resolution_y = 1000

scene.render.image_settings.file_format = 'PNG'


# ---------------------------------------------------------
# Multi-view rendering
# ---------------------------------------------------------

views = {

    "top": {
        "location": (0, 0, max_dim * 2),
        "rotation": (0, 0, 0),
    },

    "side": {
        "location": (max_dim * 2, 0, 0),
        "rotation": (radians(90), 0, radians(90)),
    },

    "front": {
        "location": (0, -max_dim * 2, 0),
        "rotation": (radians(90), 0, 0),
    },

    "back": {
        "location": (0, max_dim * 2, 0),
        "rotation": (radians(90), 0, radians(180)),
    },
}


for name, cfg in views.items():

    cam.location = cfg["location"]
    cam.rotation_euler = cfg["rotation"]

    output_path = OUTPUT_DIR / f"{name}.png"

    scene.render.filepath = str(output_path)

    print(f"Rendering {name} -> {output_path}")

    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------
# Perspective render
# ---------------------------------------------------------

cam.data.type = 'PERSP'

cam.location = (
    max_dim * 1.5,
    -max_dim * 1.5,
    max_dim
)

cam.rotation_euler = (
    radians(65),
    0,
    radians(45)
)

output_path = OUTPUT_DIR / "perspective.png"

scene.render.filepath = str(output_path)

print(f"Rendering perspective -> {output_path}")

bpy.ops.render.render(write_still=True)

print("\nAll renders complete.")
