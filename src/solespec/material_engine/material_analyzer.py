import trimesh
from PIL import Image

from src.solespec.schemas.techpack_schema import MaterialSpec


class MaterialAnalyzer:
    def analyze(self, scene: trimesh.Scene) -> list[MaterialSpec]:
        materials: dict[str, MaterialSpec] = {}
        signatures: dict[tuple, str] = {}

        for _, mesh in scene.geometry.items():
            visual = getattr(mesh, "visual", None)
            material = getattr(visual, "material", None)

            if material is None:
                continue

            material_name = getattr(material, "name", None) or "unnamed_material"

            base_color = self._extract_base_color(material)
            dominant_colors = self._extract_dominant_texture_colors(material)
            color_source_confidence = 0.45
            color_source = "unavailable"

            if base_color is None and dominant_colors:
                base_color = dominant_colors[0]
                color_source_confidence = 0.65
                color_source = "texture_dominant_color"
            elif base_color is not None:
                color_source_confidence = 0.7
                color_source = "material_base_color"

            signature = (
                material_name,
                tuple(base_color or []),
                tuple(tuple(color) for color in dominant_colors),
                color_source,
            )
            if signature in signatures:
                continue

            unique_name = self._unique_material_name(material_name, materials)
            signatures[signature] = unique_name

            materials[unique_name] = MaterialSpec(
                name=unique_name,
                base_color_rgb=base_color,
                base_color_hex=self._rgb_to_hex(base_color),
                dominant_colors_rgb=dominant_colors or ([base_color] if base_color else []),
                dominant_colors_hex=[
                    self._rgb_to_hex(color)
                    for color in (dominant_colors or ([base_color] if base_color else []))
                    if color is not None
                ],
                color_source=color_source,
                inferred_type=self._infer_material_type(material_name),
                confidence=color_source_confidence,
            )

        return list(materials.values())

    def _unique_material_name(
        self,
        material_name: str,
        materials: dict[str, MaterialSpec],
    ) -> str:
        if material_name not in materials:
            return material_name

        suffix = 2
        while f"{material_name}_{suffix}" in materials:
            suffix += 1

        return f"{material_name}_{suffix}"

    def _extract_base_color(self, material) -> list[int] | None:
        color = getattr(material, "baseColorFactor", None)

        if color is None:
            color = getattr(material, "diffuse", None)

        if color is None:
            return None

        try:
            rgb = [int(float(c) * 255) if float(c) <= 1 else int(c) for c in color[:3]]
            return [max(0, min(255, v)) for v in rgb]
        except Exception:
            return None

    def _extract_dominant_texture_colors(self, material, max_colors: int = 5) -> list[list[int]]:
        texture = getattr(material, "baseColorTexture", None) or getattr(material, "image", None)

        if texture is None:
            main_color = getattr(material, "main_color", None)
            return [self._coerce_rgb(main_color)] if main_color is not None else []

        try:
            image = texture.convert("RGBA") if isinstance(texture, Image.Image) else Image.open(texture).convert("RGBA")
        except Exception:
            return []

        image.thumbnail((256, 256))
        quantized = image.convert("RGB").quantize(colors=16, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette() or []
        counts = sorted(quantized.getcolors() or [], reverse=True)

        dominant_colors: list[list[int]] = []
        for _, palette_index in counts:
            offset = palette_index * 3
            rgb = palette[offset: offset + 3]
            if len(rgb) < 3 or self._is_background_color(rgb):
                continue
            if any(self._color_distance(rgb, existing) < 28 for existing in dominant_colors):
                continue

            dominant_colors.append([int(v) for v in rgb])
            if len(dominant_colors) >= max_colors:
                break

        return dominant_colors

    def _coerce_rgb(self, color) -> list[int]:
        rgb = [int(float(c) * 255) if float(c) <= 1 else int(c) for c in color[:3]]
        return [max(0, min(255, v)) for v in rgb]

    def _is_background_color(self, rgb: list[int]) -> bool:
        r, g, b = rgb[:3]
        return (
            max(rgb) > 242 and min(rgb) > 225
        ) or (
            max(rgb) < 12
        ) or (
            abs(r - g) < 4 and abs(g - b) < 4 and r > 235
        )

    def _color_distance(self, left: list[int], right: list[int]) -> float:
        return sum((left[index] - right[index]) ** 2 for index in range(3)) ** 0.5

    def _rgb_to_hex(self, rgb: list[int] | None) -> str | None:
        if not rgb:
            return None

        return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])

    def _infer_material_type(self, material_name: str) -> str:
        name = material_name.lower()

        if "rubber" in name or "sole" in name:
            return "rubber"
        if "mesh" in name:
            return "mesh"
        if "leather" in name:
            return "leather"
        if "foam" in name or "eva" in name:
            return "foam"

        return "synthetic_or_unknown"
