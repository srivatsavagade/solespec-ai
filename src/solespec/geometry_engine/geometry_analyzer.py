import numpy as np
import trimesh

from src.solespec.schemas.techpack_schema import MeasurementSpec, ComponentSpec


class GeometryAnalyzer:
    def analyze_measurements(self, scene: trimesh.Scene) -> MeasurementSpec:
        bounds = scene.bounds

        if bounds is None:
            return MeasurementSpec()

        min_xyz, max_xyz = bounds
        size_m = max_xyz - min_xyz
        size_mm = size_m * 1000.0

        return MeasurementSpec(
            length_mm=float(size_mm[0]),
            height_mm=float(size_mm[1]),
            width_mm=float(size_mm[2]),
            heel_height_mm=0.0,
            sole_thickness_mm=float(size_mm[2] * 0.18),
        )

    def extract_components(self, scene: trimesh.Scene) -> list[ComponentSpec]:
        components: list[ComponentSpec] = []

        transformed_meshes = scene.dump()

        for index, mesh in enumerate(transformed_meshes):
            if not isinstance(mesh, trimesh.Trimesh):
                continue

            mesh_name = (
                mesh.metadata.get("name")
                or mesh.metadata.get("node")
                or f"mesh_{index}"
            )

            if not hasattr(mesh, "bounds") or mesh.bounds is None:
                continue

            min_xyz, max_xyz = mesh.bounds
            bbox_mm = (max_xyz - min_xyz) * 1000.0

            inferred_name = self._infer_component_name(mesh_name, bbox_mm)

            material_name = None
            if hasattr(mesh.visual, "material") and mesh.visual.material is not None:
                material_name = getattr(mesh.visual.material, "name", None)

            components.append(
                ComponentSpec(
                    name=inferred_name,
                    mesh_name=mesh_name,
                    bbox_mm={
                        "length": float(bbox_mm[0]),
                        "height": float(bbox_mm[1]),
                        "width": float(bbox_mm[2]),
                    },
                    material_name=material_name,
                    confidence=0.6,
                    notes="Heuristic component classification from mesh name and bounding box.",
                )
            )

        return components

    def _infer_component_name(self, mesh_name: str, bbox_mm: np.ndarray) -> str:
        name = mesh_name.lower()

        if "sole" in name:
            return "sole"
        if "lace" in name:
            return "laces"
        if "tongue" in name:
            return "tongue"
        if "upper" in name:
            return "upper"

        height = bbox_mm[1]
        length = bbox_mm[0]

        if height < 0.25 * max(length, 1):
            return "sole_or_low_profile_component"

        return "unknown_component"
