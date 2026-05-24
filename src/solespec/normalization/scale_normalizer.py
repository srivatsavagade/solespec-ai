import numpy as np
import trimesh


class ScaleNormalizer:
    """
    Rescales footwear models into plausible manufacturing dimensions.

    Assumption:
    If the model has no reliable unit metadata, normalize longest axis
    to a typical footwear length of 280 mm.
    """

    def __init__(
        self,
        target_length_mm: float = 280.0,
        min_plausible_mm: float = 180.0,
        max_plausible_mm: float = 380.0,
    ):
        self.target_length_mm = target_length_mm
        self.min_plausible_mm = min_plausible_mm
        self.max_plausible_mm = max_plausible_mm

    def normalize(self, scene: trimesh.Scene) -> tuple[trimesh.Scene, dict]:
        scene = scene.copy()

        bounds = scene.bounds
        size_units = bounds[1] - bounds[0]

        length_units = float(size_units[0])  # after orientation: X = length
        if length_units <= 0:
            raise ValueError(
                "Cannot normalize scale because the scene has zero length on the X axis."
            )

        length_mm_assuming_meters = length_units * 1000.0

        metadata = {
            "scale_applied": False,
            "original_length_mm_assuming_meters": round(length_mm_assuming_meters, 2),
            "target_length_mm": self.target_length_mm,
            "scale_factor": 1.0,
            "reason": "Length already plausible.",
        }

        if self.min_plausible_mm <= length_mm_assuming_meters <= self.max_plausible_mm:
            return scene, metadata

        target_length_units = self.target_length_mm / 1000.0
        scale_factor = target_length_units / length_units

        transform = np.eye(4)
        transform[:3, :3] *= scale_factor

        scene.apply_transform(transform)

        metadata.update(
            {
                "scale_applied": True,
                "scale_factor": scale_factor,
                "reason": (
                    "Input units produced implausible footwear dimensions; "
                    "rescaled longest axis to target footwear length."
                ),
            }
        )

        return scene, metadata
