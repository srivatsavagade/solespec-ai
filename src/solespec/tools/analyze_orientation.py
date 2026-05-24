import trimesh
import numpy as np


def analyze_orientation(glb_path="input/used_new_balance_574_classic______free.glb"):

    scene = trimesh.load(glb_path, force="scene")

    bounds = scene.bounds

    min_corner, max_corner = bounds

    size = max_corner - min_corner

    axes = ["X", "Y", "Z"]

    print("\nMODEL DIMENSIONS")
    print("=" * 50)

    for axis, value in zip(axes, size):
        print(f"{axis}: {value:.4f}")

    dominant_axis = axes[np.argmax(size)]

    print("\nDominant Axis:", dominant_axis)

    print("\nInterpretation:")

    if dominant_axis == "X":
        print("Likely shoe length axis = X")

    elif dominant_axis == "Y":
        print("Likely shoe length axis = Y")

    else:
        print("Likely shoe length axis = Z")


if __name__ == "__main__":
    analyze_orientation()

'''“Different DCC tools export footwear assets with inconsistent coordinate conventions, so the pipeline standardizes models into a canonical orientation before analysis.”'''
