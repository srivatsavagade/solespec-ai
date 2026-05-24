import numpy as np
import trimesh


class SceneNormalizer:
    """
    Converts incoming footwear assets into a canonical coordinate system.

    Canonical convention:
    - X axis = shoe length
    - Y axis = vertical height
    - Z axis = shoe width

    This is necessary because GLB exports from different tools may use
    different axis conventions.
    """

    def normalize(self, scene: trimesh.Scene) -> trimesh.Scene:
        scene = scene.copy()

        self._center_scene(scene)
        self._align_longest_axis_to_x(scene)
        self._align_height_axis_to_y(scene)
        self._move_bottom_to_ground(scene)

        return scene

    def _center_scene(self, scene: trimesh.Scene) -> None:
        bounds = scene.bounds
        center = bounds.mean(axis=0)

        transform = np.eye(4)
        transform[:3, 3] = -center

        scene.apply_transform(transform)

    def _align_longest_axis_to_x(self, scene: trimesh.Scene) -> None:
        bounds = scene.bounds
        size = bounds[1] - bounds[0]

        length_axis = int(np.argmax(size))

        # If longest axis already X, no rotation needed.
        if length_axis == 0:
            return

        transform = np.eye(4)

        # Y -> X
        if length_axis == 1:
            # new X = old Y, new Y = old X
            transform[:3, :3] = np.array([
                [0, 1, 0],
                [1, 0, 0],
                [0, 0, 1],
            ])

        # Z -> X
        elif length_axis == 2:
            # new X = old Z, new Z = old X
            transform[:3, :3] = np.array([
                [0, 0, 1],
                [0, 1, 0],
                [1, 0, 0],
            ])

        scene.apply_transform(transform)

    def _align_height_axis_to_y(self, scene: trimesh.Scene) -> None:
        """
        After longest-axis alignment, choose the larger of remaining axes
        as vertical height only as a fallback.

        For the current asset, old Y appears to be height-like after Z->X
        rotation, so this method mainly keeps the convention explicit.
        """
        bounds = scene.bounds
        size = bounds[1] - bounds[0]

        # X is length. Between Y and Z, height is often the larger vertical
        # body dimension for shoe side profile. Width is usually smaller.
        yz_sizes = size[1:3]
        height_relative_axis = int(np.argmax(yz_sizes)) + 1

        if height_relative_axis == 1:
            return

        # Swap Y and Z if needed.
        transform = np.eye(4)
        transform[:3, :3] = np.array([
            [1, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
        ])

        scene.apply_transform(transform)

    def _move_bottom_to_ground(self, scene: trimesh.Scene) -> None:
        bounds = scene.bounds
        min_y = bounds[0][1]

        transform = np.eye(4)
        transform[1, 3] = -min_y

        scene.apply_transform(transform)
