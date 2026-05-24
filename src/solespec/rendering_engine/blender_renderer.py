from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import textwrap

from src.solespec.schemas.techpack_schema import RenderSpec


class BlenderRenderer:
    def __init__(self, blender_executable: str | None = None):
        self.blender_executable = self._resolve_blender_executable(blender_executable)

    def render_views(
        self,
        glb_path: Path,
        output_dir: Path,
    ) -> list[RenderSpec]:

        if not glb_path.exists():
            raise FileNotFoundError(f"Render input GLB not found: {glb_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        blender_script = self._generate_blender_script(
            glb_path=glb_path,
            output_dir=output_dir,
        )

        with tempfile.NamedTemporaryFile(
            suffix=".py",
            delete=False,
            mode="w",
            encoding="utf-8",
        ) as tmp:
            tmp.write(blender_script)
            tmp_script_path = tmp.name

        command = [
            self.blender_executable,
            "--background",
            "--python",
            tmp_script_path,
        ]

        print("\nRunning Blender multi-view renderer...")
        subprocess.run(command, check=True)
        print("Blender rendering complete.")

        views = [
            "top",
            "side",
            "front",
            "back",
            "perspective",
        ]

        return [
            RenderSpec(
                view_name=view,
                image_path=str(output_dir / f"{view}.png"),
            )
            for view in views
        ]

    def _resolve_blender_executable(self, configured_path: str | None) -> str:
        candidates = [
            configured_path,
            os.environ.get("BLENDER_EXECUTABLE"),
            shutil.which("blender"),
        ]

        for candidate in candidates:
            if not candidate:
                continue

            path = Path(candidate)
            if path.exists():
                return str(path)

            if shutil.which(candidate):
                return candidate

        raise FileNotFoundError(
            "Blender executable not found. Set BLENDER_EXECUTABLE or pass "
            "blender_executable when constructing BlenderRenderer."
        )

    def _generate_blender_script(
        self,
        glb_path: Path,
        output_dir: Path,
    ) -> str:

        return textwrap.dedent(
            f"""
            import bpy
            from pathlib import Path
            from math import radians
            from mathutils import Vector


            GLB_PATH = r"{glb_path.resolve()}"
            OUTPUT_DIR = Path(r"{output_dir.resolve()}")
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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

            def compute_bounds(objects):
                min_corner = [float("inf")] * 3
                max_corner = [float("-inf")] * 3

                for obj in objects:
                    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

                    for v in bbox:
                        for i in range(3):
                            min_corner[i] = min(min_corner[i], v[i])
                            max_corner[i] = max(max_corner[i], v[i])

                size = [
                    max_corner[i] - min_corner[i]
                    for i in range(3)
                ]

                center = [
                    (min_corner[i] + max_corner[i]) / 2
                    for i in range(3)
                ]

                return min_corner, max_corner, size, center


            min_corner, max_corner, size, center = compute_bounds(objs)


            # ---------------------------------------------------------
            # Center meshes around origin
            # ---------------------------------------------------------

            for obj in objs:
                obj.location.x -= center[0]
                obj.location.y -= center[1]
                obj.location.z -= center[2]

            bpy.context.view_layer.update()
            min_corner, max_corner, size, center = compute_bounds(objs)
            max_dim = max(size)
            min_z = min_corner[2]
            target = Vector(center)


            def look_at(obj, target):
                direction = target - obj.location
                obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


            # ---------------------------------------------------------
            # Camera setup
            # ---------------------------------------------------------

            cam_data = bpy.data.cameras.new(name="Camera")
            cam = bpy.data.objects.new("Camera", cam_data)

            bpy.context.collection.objects.link(cam)
            bpy.context.scene.camera = cam

            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = max_dim * 1.18


            # ---------------------------------------------------------
            # Lighting
            # ---------------------------------------------------------

            light_data = bpy.data.lights.new(name="Key_Area", type='AREA')
            light = bpy.data.objects.new(name="Key_Area", object_data=light_data)

            bpy.context.collection.objects.link(light)

            light.location = (max_dim * 1.5, -max_dim * 1.4, max_dim * 2)
            light.data.energy = 450
            light.data.size = max_dim * 2.2

            fill_data = bpy.data.lights.new(name="Fill", type='POINT')
            fill = bpy.data.objects.new(name="Fill", object_data=fill_data)
            bpy.context.collection.objects.link(fill)
            fill.location = (-max_dim, max_dim, max_dim)
            fill.data.energy = 60

            bpy.ops.mesh.primitive_plane_add(size=max_dim * 2.4, location=(0, 0, min_z - max_dim * 0.015))
            plane = bpy.context.object
            plane.name = "Matte_Reference_Ground"
            mat = bpy.data.materials.new("Warm_White_Backdrop")
            mat.diffuse_color = (0.94, 0.94, 0.91, 1)
            plane.data.materials.append(mat)


            # ---------------------------------------------------------
            # Render settings
            # ---------------------------------------------------------

            scene = bpy.context.scene

            scene.render.engine = 'CYCLES'
            scene.cycles.samples = 64
            scene.view_settings.view_transform = 'Filmic'
            scene.view_settings.look = 'Medium High Contrast'
            scene.world.color = (1, 1, 1)

            scene.render.resolution_x = 1400
            scene.render.resolution_y = 1000

            scene.render.image_settings.file_format = 'PNG'


            # ---------------------------------------------------------
            # Multi-view rendering
            # ---------------------------------------------------------

            views = {{

                "top": {{
                    "location": (center[0], center[1], center[2] + max_dim * 2),
                }},

                "side": {{
                    "location": (center[0], center[1] - max_dim * 2, center[2]),
                }},

                "front": {{
                    "location": (center[0] + max_dim * 2, center[1], center[2]),
                }},

                "back": {{
                    "location": (center[0] - max_dim * 2, center[1], center[2]),
                }},
            }}


            for name, cfg in views.items():
                cam.data.type = 'ORTHO'
                cam.data.ortho_scale = max_dim * 1.18

                cam.location = cfg["location"]
                look_at(cam, target)

                output_path = OUTPUT_DIR / f"{{name}}.png"

                scene.render.filepath = str(output_path)

                print(f"Rendering {{name}} -> {{output_path}}")

                bpy.ops.render.render(write_still=True)


            # ---------------------------------------------------------
            # Perspective render
            # ---------------------------------------------------------

            cam.data.type = 'PERSP'

            cam.location = (
                center[0] + max_dim * 1.5,
                center[1] - max_dim * 1.5,
                center[2] + max_dim,
            )

            look_at(cam, target)

            output_path = OUTPUT_DIR / "perspective.png"

            scene.render.filepath = str(output_path)

            print(f"Rendering perspective -> {{output_path}}")

            bpy.ops.render.render(write_still=True)

            print("\\nAll renders complete.")
            """
        )
