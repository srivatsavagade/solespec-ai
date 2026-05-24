from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from src.solespec.schemas.techpack_schema import MeasurementSpec, RenderSpec


class TechnicalDrawingGenerator:
    def generate_drawings(
        self,
        renders: list[RenderSpec],
        output_dir: Path,
        measurements: MeasurementSpec,
    ) -> list[RenderSpec]:
        output_dir.mkdir(parents=True, exist_ok=True)
        drawings: list[RenderSpec] = []

        for view_name in ["side", "top", "front"]:
            render = self._find_render(renders, view_name)
            if render is None:
                continue

            output_path = output_dir / f"{view_name}_technical_drawing.png"
            self.generate_drawing(
                image_path=Path(render.image_path),
                output_path=output_path,
                view_name=view_name,
                measurements=measurements,
            )
            drawings.append(
                RenderSpec(
                    view_name=f"technical_{view_name}",
                    image_path=str(output_path),
                )
            )

        return drawings

    def generate_drawing(
        self,
        image_path: Path,
        output_path: Path,
        view_name: str,
        measurements: MeasurementSpec,
    ) -> None:
        source = Image.open(image_path).convert("RGB")
        drawing = self._line_art(source)
        drawing = self._add_border_and_title(drawing, view_name)

        if view_name == "side":
            self._draw_side_measurements(drawing, measurements)
        elif view_name == "top":
            self._draw_top_measurements(drawing, measurements)
        elif view_name == "front":
            self._draw_front_measurements(drawing, measurements)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        drawing.save(output_path)

    def _line_art(self, image: Image.Image) -> Image.Image:
        image = self._crop_render_background(image)
        gray = ImageOps.grayscale(image)
        gray = ImageEnhance.Contrast(gray).enhance(1.7)
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageOps.autocontrast(edges)

        # Black edge lines on a white technical drawing background.
        return edges.point(lambda value: 0 if value > 28 else 255).convert("RGB")

    def _add_border_and_title(self, image: Image.Image, view_name: str) -> Image.Image:
        canvas = Image.new("RGB", (1400, 1000), "white")
        image.thumbnail((1180, 740))
        canvas.paste(image, ((canvas.width - image.width) // 2, 135))

        draw = ImageDraw.Draw(canvas)
        title_font, label_font = self._fonts()
        draw.rectangle((42, 42, canvas.width - 42, canvas.height - 42), outline=(20, 20, 20), width=3)
        draw.line((42, 112, canvas.width - 42, 112), fill=(20, 20, 20), width=2)
        draw.text((68, 66), f"{view_name.upper()} TECHNICAL DRAWING", fill=(10, 10, 10), font=title_font)
        draw.text((canvas.width - 300, 72), "Units: mm", fill=(60, 60, 60), font=label_font)

        return canvas

    def _draw_side_measurements(self, image: Image.Image, measurements: MeasurementSpec) -> None:
        draw = ImageDraw.Draw(image)
        _, label_font = self._fonts()
        self._dimension_arrow(
            draw,
            start=(150, 885),
            end=(1250, 885),
            label=f"Length {self._fmt(measurements.length_mm)}",
            label_xy=(560, 830),
            font=label_font,
        )
        self._dimension_arrow(
            draw,
            start=(118, 220),
            end=(118, 790),
            label=f"Height {self._fmt(measurements.height_mm)}",
            label_xy=(150, 485),
            font=label_font,
        )
        draw.text(
            (945, 170),
            f"Heel lift est. {self._fmt(measurements.heel_height_mm)}",
            fill=(20, 20, 20),
            font=label_font,
        )

    def _draw_top_measurements(self, image: Image.Image, measurements: MeasurementSpec) -> None:
        draw = ImageDraw.Draw(image)
        _, label_font = self._fonts()
        draw.text(
            (72, 880),
            f"Top reference: length {self._fmt(measurements.length_mm)}, width {self._fmt(measurements.width_mm)}",
            fill=(20, 20, 20),
            font=label_font,
        )

    def _draw_front_measurements(self, image: Image.Image, measurements: MeasurementSpec) -> None:
        draw = ImageDraw.Draw(image)
        _, label_font = self._fonts()
        draw.text(
            (72, 880),
            f"Front reference: width {self._fmt(measurements.width_mm)}, height {self._fmt(measurements.height_mm)}",
            fill=(20, 20, 20),
            font=label_font,
        )

    def _dimension_arrow(
        self,
        draw: ImageDraw.ImageDraw,
        start: tuple[int, int],
        end: tuple[int, int],
        label: str,
        label_xy: tuple[int, int],
        font: ImageFont.ImageFont,
    ) -> None:
        draw.line((*start, *end), fill=(15, 15, 15), width=4)

        if start[1] == end[1]:
            draw.polygon([(start[0], start[1]), (start[0] + 22, start[1] - 12), (start[0] + 22, start[1] + 12)], fill=(15, 15, 15))
            draw.polygon([(end[0], end[1]), (end[0] - 22, end[1] - 12), (end[0] - 22, end[1] + 12)], fill=(15, 15, 15))
        else:
            draw.polygon([(start[0], start[1]), (start[0] - 12, start[1] + 22), (start[0] + 12, start[1] + 22)], fill=(15, 15, 15))
            draw.polygon([(end[0], end[1]), (end[0] - 12, end[1] - 22), (end[0] + 12, end[1] - 22)], fill=(15, 15, 15))

        draw.rounded_rectangle(
            (label_xy[0] - 10, label_xy[1] - 6, label_xy[0] + 245, label_xy[1] + 32),
            radius=6,
            fill="white",
            outline=(15, 15, 15),
            width=1,
        )
        draw.text(label_xy, label, fill=(15, 15, 15), font=font)

    def _crop_render_background(self, image: Image.Image) -> Image.Image:
        gray = image.convert("L")
        bbox = gray.point(lambda value: 255 if value > 88 else 0).getbbox()
        if bbox is None:
            return image

        left, top, right, bottom = bbox
        margin = 42
        left = max(0, left - margin)
        top = max(0, top - margin)
        right = min(image.width, right + margin)
        bottom = min(image.height, bottom + margin)

        if right - left < image.width * 0.25 or bottom - top < image.height * 0.25:
            return image

        return image.crop((left, top, right, bottom))

    def _find_render(self, renders: list[RenderSpec], view_name: str) -> RenderSpec | None:
        for render in renders:
            if render.view_name == view_name:
                return render
        return None

    def _fmt(self, value: float | None) -> str:
        if value is None:
            return "n/a"
        return f"{value:.0f} mm"

    def _fonts(self) -> tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
        try:
            return (
                ImageFont.truetype("arialbd.ttf", 32),
                ImageFont.truetype("arial.ttf", 24),
            )
        except OSError:
            fallback = ImageFont.load_default()
            return fallback, fallback
