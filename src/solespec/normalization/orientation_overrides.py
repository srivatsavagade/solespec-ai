import json
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


def load_orientation_overrides(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def apply_orientation_overrides(
    scene: trimesh.Scene,
    input_path: Path,
    overrides: dict[str, Any],
) -> tuple[trimesh.Scene, dict[str, Any]]:
    asset_overrides = overrides.get("assets", {})
    override = asset_overrides.get(input_path.stem)

    if not override:
        return scene, {"applied": False}

    scene = scene.copy()
    operations = override.get("operations", [])
    applied_operations: list[str] = []

    for operation in operations:
        if operation == "swap_yz":
            _swap_yz(scene)
            applied_operations.append(operation)
        else:
            raise ValueError(
                f"Unsupported orientation override operation for {input_path.name}: {operation}"
            )

    _move_bottom_to_ground(scene)

    return scene, {
        "applied": bool(applied_operations),
        "asset": input_path.stem,
        "operations": applied_operations,
        "reason": override.get("reason", "Manual orientation override."),
    }


def _swap_yz(scene: trimesh.Scene) -> None:
    transform = np.eye(4)
    transform[:3, :3] = np.array(
        [
            [1, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
        ]
    )
    scene.apply_transform(transform)


def _move_bottom_to_ground(scene: trimesh.Scene) -> None:
    bounds = scene.bounds
    min_y = bounds[0][1]

    transform = np.eye(4)
    transform[1, 3] = -min_y
    scene.apply_transform(transform)
