import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import trimesh

from src.solespec.geometry_engine.footwear_measurements import FootwearMeasurementEngine
from src.solespec.geometry_engine.geometry_analyzer import GeometryAnalyzer
from src.solespec.material_engine.material_analyzer import MaterialAnalyzer
from src.solespec.normalization.orientation_overrides import apply_orientation_overrides
from src.solespec.normalization.scale_normalizer import ScaleNormalizer
from src.solespec.review.overrides import apply_review_overrides
from src.solespec.schemas.techpack_schema import ComponentSpec, MaterialSpec
from src.solespec.rendering_engine.blender_renderer import BlenderRenderer
from src.solespec.utils.scene_export import export_scene_glb


WRITABLE_TMP = Path("C:/tmp")
WRITABLE_TMP.mkdir(parents=True, exist_ok=True)


class GeometryAnalyzerTests(unittest.TestCase):
    def test_low_profile_component_uses_y_axis_as_height(self):
        analyzer = GeometryAnalyzer()

        component_name = analyzer._infer_component_name(
            "mesh",
            bbox_mm=[100.0, 10.0, 80.0],
        )

        self.assertEqual(component_name, "sole_or_low_profile_component")


class ScaleNormalizerTests(unittest.TestCase):
    def test_zero_length_scene_raises_clear_error(self):
        mesh = trimesh.Trimesh(
            vertices=[
                [0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            faces=[[0, 1, 2]],
        )
        scene = trimesh.Scene(mesh)

        with self.assertRaisesRegex(ValueError, "zero length"):
            ScaleNormalizer().normalize(scene)


class OrientationOverrideTests(unittest.TestCase):
    def test_swap_yz_orientation_override_is_asset_scoped(self):
        mesh = trimesh.creation.box(extents=[2.0, 4.0, 6.0])
        scene = trimesh.Scene(mesh)

        corrected, metadata = apply_orientation_overrides(
            scene=scene,
            input_path=Path("flower_sneakers_shoe_scan.glb"),
            overrides={
                "assets": {
                    "flower_sneakers_shoe_scan": {
                        "operations": ["swap_yz"],
                        "reason": "test",
                    }
                }
            },
        )

        corrected_size = corrected.bounds[1] - corrected.bounds[0]
        self.assertTrue(metadata["applied"])
        self.assertEqual(metadata["operations"], ["swap_yz"])
        self.assertAlmostEqual(corrected_size[1], 6.0)
        self.assertAlmostEqual(corrected_size[2], 4.0)

    def test_missing_orientation_override_does_not_modify_scene(self):
        mesh = trimesh.creation.box(extents=[2.0, 4.0, 6.0])
        scene = trimesh.Scene(mesh)

        corrected, metadata = apply_orientation_overrides(
            scene=scene,
            input_path=Path("other_asset.glb"),
            overrides={
                "assets": {
                    "flower_sneakers_shoe_scan": {
                        "operations": ["swap_yz"],
                    }
                }
            },
        )

        self.assertFalse(metadata["applied"])
        self.assertTrue((corrected.bounds == scene.bounds).all())


class FootwearMeasurementEngineTests(unittest.TestCase):
    def test_flat_sole_does_not_use_rear_upper_height_as_heel_height(self):
        mesh = trimesh.creation.box(extents=[0.28, 0.12, 0.10])
        scene = trimesh.Scene(mesh)

        measurements = FootwearMeasurementEngine().analyze(scene)

        self.assertEqual(measurements.length_mm, 280.0)
        self.assertEqual(measurements.heel_height_mm, 0.0)


class MaterialAnalyzerTests(unittest.TestCase):
    def test_same_named_materials_with_different_colors_are_preserved(self):
        scene = SimpleNamespace(
            geometry={
                "mesh_a": SimpleNamespace(
                    visual=SimpleNamespace(
                        material=SimpleNamespace(name="shared", diffuse=[1.0, 0.0, 0.0])
                    )
                ),
                "mesh_b": SimpleNamespace(
                    visual=SimpleNamespace(
                        material=SimpleNamespace(name="shared", diffuse=[0.0, 0.0, 1.0])
                    )
                ),
            }
        )

        materials = MaterialAnalyzer().analyze(scene)

        self.assertEqual([material.name for material in materials], ["shared", "shared_2"])
        self.assertEqual(
            [material.base_color_hex for material in materials],
            ["#FF0000", "#0000FF"],
        )


class ReviewOverrideTests(unittest.TestCase):
    def test_review_overrides_patch_components_and_materials(self):
        components = [
            ComponentSpec(
                name="unknown_component",
                mesh_name="Object_0",
                bbox_mm={"length": 280.0, "height": 120.0, "width": 100.0},
                material_name="material_0",
                confidence=0.6,
            )
        ]
        materials = [
            MaterialSpec(
                name="material_0",
                base_color_hex="#FFFFFF",
                confidence=0.65,
            )
        ]

        patched_components, patched_materials, notes = apply_review_overrides(
            components,
            materials,
            {
                "components": [
                    {
                        "match": {"mesh_name": "Object_0"},
                        "name": "upper",
                        "material_name": "reviewed_mesh",
                        "confidence": 0.9,
                    }
                ],
                "materials": [
                    {
                        "match": {"name": "material_0"},
                        "name": "reviewed_mesh",
                        "inferred_type": "mesh",
                        "confidence": 0.9,
                    }
                ],
                "notes": ["Human review applied."],
            },
        )

        self.assertEqual(patched_components[0].name, "upper")
        self.assertEqual(patched_components[0].material_name, "reviewed_mesh")
        self.assertEqual(patched_materials[0].name, "reviewed_mesh")
        self.assertEqual(patched_materials[0].inferred_type, "mesh")
        self.assertIn("Human review applied.", notes)


class SceneExportTests(unittest.TestCase):
    def test_export_scene_glb_writes_file(self):
        class FakeScene:
            def export(self, output_path):
                Path(output_path).write_bytes(b"glb")

        with tempfile.TemporaryDirectory(dir=WRITABLE_TMP) as tmpdir:
            output_path = export_scene_glb(FakeScene(), Path(tmpdir) / "normalized.glb")

            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)


class BlenderRendererTests(unittest.TestCase):
    def test_blender_path_can_be_resolved_from_environment(self):
        with tempfile.TemporaryDirectory(dir=WRITABLE_TMP) as tmpdir:
            fake_blender = Path(tmpdir) / "blender.exe"
            fake_blender.write_text("", encoding="utf-8")

            previous = os.environ.get("BLENDER_EXECUTABLE")
            os.environ["BLENDER_EXECUTABLE"] = str(fake_blender)
            try:
                renderer = BlenderRenderer()
            finally:
                if previous is None:
                    os.environ.pop("BLENDER_EXECUTABLE", None)
                else:
                    os.environ["BLENDER_EXECUTABLE"] = previous

            self.assertEqual(renderer.blender_executable, str(fake_blender))


if __name__ == "__main__":
    unittest.main()
