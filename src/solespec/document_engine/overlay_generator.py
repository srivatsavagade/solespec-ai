from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from src.solespec.schemas.techpack_schema import MeasurementSpec, RenderSpec


class OverlayGenerator:
    def generate_measurement_overlays(
        self,
        renders: list[RenderSpec],
        output_dir: Path,
        measurements: MeasurementSpec,
    ) -> list[RenderSpec]:
        annotated: list[RenderSpec] = []
        side_render = self._find_render(renders, "side")

        if side_render is None:
            return annotated

        output_path = output_dir / "side_measurements.png"

        self.generate_measurement_overlay(
            image_path=Path(side_render.image_path),
            output_path=output_path,
            measurements=measurements,
        )

        annotated.append(
            RenderSpec(
                view_name="side_measurements",
                image_path=str(output_path),
            )
        )

        return annotated

    def generate_measurement_overlay(
        self,
        image_path: Path,
        output_path: Path,
        measurements: MeasurementSpec,
    ) -> None:

        image = Image.open(image_path).convert("RGB")

        draw = ImageDraw.Draw(image)

        width, height = image.size

        try:
            label_font = ImageFont.truetype("arial.ttf", 34)
            small_font = ImageFont.truetype("arial.ttf", 26)
        except OSError:
            label_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        try:
            title_font = ImageFont.truetype("arialbd.ttf", 36)
        except OSError:
            font = ImageFont.load_default()
            title_font = font

        line_color = (210, 26, 26)
        text_color = (20, 20, 20)
        box_fill = (255, 255, 255)
        box_outline = (210, 26, 26)

        # ---------------------------------------------------------
        # Length Arrow
        # ---------------------------------------------------------

        y = height - 110

        x1 = 120
        x2 = width - 120

        draw.line((x1, y, x2, y), fill=line_color, width=7)

        draw.polygon(
            [
                (x1, y),
                (x1 + 28, y - 15),
                (x1 + 28, y + 15),
            ],
            fill=line_color,
        )

        draw.polygon(
            [
                (x2, y),
                (x2 - 28, y - 15),
                (x2 - 28, y + 15),
            ],
            fill=line_color,
        )

        length_text = f"Length {measurements.length_mm:.0f} mm"
        self._draw_label(
            draw=draw,
            xy=((width // 2) - 135, y - 64),
            text=length_text,
            font=label_font,
            fill=box_fill,
            outline=box_outline,
            text_color=text_color,
        )

        # ---------------------------------------------------------
        # Height Arrow
        # ---------------------------------------------------------

        x = 110

        y1 = 120
        y2 = height - 190

        draw.line((x, y1, x, y2), fill=line_color, width=7)

        draw.polygon(
            [
                (x, y1),
                (x - 15, y1 + 28),
                (x + 15, y1 + 28),
            ],
            fill=line_color,
        )

        draw.polygon(
            [
                (x, y2),
                (x - 15, y2 - 28),
                (x + 15, y2 - 28),
            ],
            fill=line_color,
        )

        height_text = f"Height {measurements.height_mm:.0f} mm"
        self._draw_label(
            draw=draw,
            xy=(x + 36, (height // 2) - 24),
            text=height_text,
            font=small_font,
            fill=box_fill,
            outline=box_outline,
            text_color=text_color,
        )

        # ---------------------------------------------------------
        # Heel Height Label
        # ---------------------------------------------------------

        heel_text = (
            f"Heel height "
            f"{measurements.heel_height_mm:.0f} mm"
        )

        self._draw_label(
            draw=draw,
            xy=(width - 430, 76),
            text=heel_text,
            font=small_font,
            fill=box_fill,
            outline=(40, 90, 180),
            text_color=(40, 70, 150),
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        image.save(output_path)

        print(f"Saved overlay: {output_path}")

    def _draw_label(
        self,
        draw: ImageDraw.ImageDraw,
        xy: tuple[int, int],
        text: str,
        font: ImageFont.ImageFont,
        fill: tuple[int, int, int],
        outline: tuple[int, int, int],
        text_color: tuple[int, int, int],
    ) -> None:
        x, y = xy
        padding_x = 14
        padding_y = 8
        bbox = draw.textbbox((x, y), text, font=font)
        rect = (
            bbox[0] - padding_x,
            bbox[1] - padding_y,
            bbox[2] + padding_x,
            bbox[3] + padding_y,
        )

        draw.rounded_rectangle(rect, radius=8, fill=fill, outline=outline, width=2)
        draw.text((x, y), text, fill=text_color, font=font)

    def _find_render(
        self,
        renders: list[RenderSpec],
        view_name: str,
    ) -> RenderSpec | None:
        for render in renders:
            if render.view_name == view_name:
                return render

        return None
