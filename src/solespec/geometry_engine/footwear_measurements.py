import numpy as np
import trimesh

from src.solespec.schemas.techpack_schema import MeasurementSpec


class FootwearMeasurementEngine:
    """
    Geometry-aware footwear measurements.

    Canonical coordinate convention:
    - X = length
    - Y = height
    - Z = width
    """

    def analyze(self, scene: trimesh.Scene) -> MeasurementSpec:

        mesh = self._merge_scene(scene)

        vertices = mesh.vertices

        x = vertices[:, 0]
        y = vertices[:, 1]
        z = vertices[:, 2]

        # ---------------------------------------------------------
        # Global dimensions
        # ---------------------------------------------------------

        length_mm = (x.max() - x.min()) * 1000
        height_mm = (y.max() - y.min()) * 1000
        width_mm = (z.max() - z.min()) * 1000

        # ---------------------------------------------------------
        # Heel lift estimate
        # Difference between rear and forefoot lower envelopes.
        # ---------------------------------------------------------

        x_min = x.min()
        x_max = x.max()

        length_units = x_max - x_min
        rear_threshold = x_min + length_units * 0.15
        forefoot_threshold = x_max - length_units * 0.25

        rear_y = y[x <= rear_threshold]
        forefoot_y = y[x >= forefoot_threshold]

        if len(rear_y) > 0 and len(forefoot_y) > 0:
            rear_lower_envelope = np.percentile(rear_y, 5)
            forefoot_lower_envelope = np.percentile(forefoot_y, 5)
            heel_height_mm = max(0.0, (rear_lower_envelope - forefoot_lower_envelope) * 1000)
        else:
            heel_height_mm = 0.0

        # ---------------------------------------------------------
        # Sole thickness estimation
        # Lower 10% vertical band
        # ---------------------------------------------------------

        y_min = y.min()
        y_max = y.max()

        lower_band_threshold = y_min + (y_max - y_min) * 0.10

        sole_vertices = y[y <= lower_band_threshold]

        if len(sole_vertices) > 0:
            sole_thickness_mm = (
                sole_vertices.max() - sole_vertices.min()
            ) * 1000
        else:
            sole_thickness_mm = height_mm * 0.12

        return MeasurementSpec(
            length_mm=round(float(length_mm), 2),
            width_mm=round(float(width_mm), 2),
            height_mm=round(float(height_mm), 2),
            heel_height_mm=round(float(heel_height_mm), 2),
            sole_thickness_mm=round(float(sole_thickness_mm), 2),
        )

    def _merge_scene(self, scene: trimesh.Scene) -> trimesh.Trimesh:
        # Use Scene.dump so node transforms from orientation/scale normalization
        # are applied before measuring vertices.
        merged = scene.dump(concatenate=True)

        if merged is None or not isinstance(merged, trimesh.Trimesh):
            raise ValueError("No meshes found in scene")

        return merged
