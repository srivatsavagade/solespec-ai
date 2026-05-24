from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from src.solespec.schemas.techpack_schema import RenderSpec


class RenderGenerator:
    def generate_placeholder_renders(self, output_dir: Path) -> list[RenderSpec]:
        output_dir.mkdir(parents=True, exist_ok=True)

        views = ["top", "side", "front", "back", "three_quarter"]
        renders: list[RenderSpec] = []

        for view in views:
            image_path = output_dir / f"{view}.png"
            self._create_placeholder(image_path, view)
            renders.append(RenderSpec(view_name=view, image_path=str(image_path)))

        return renders

    def _create_placeholder(self, image_path: Path, view: str) -> None:
        img = Image.new("RGB", (1200, 800), "white")
        draw = ImageDraw.Draw(img)

        draw.rectangle((100, 100, 1100, 700), outline="black", width=3)
        draw.text((450, 380), f"{view.upper()} VIEW", fill="black")

        img.save(image_path)
