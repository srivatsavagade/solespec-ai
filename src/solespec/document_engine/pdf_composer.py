from pathlib import Path
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import Image

from src.solespec.schemas.techpack_schema import RenderSpec, TechPackSpec


class PDFComposer:
    margin = 18 * mm
    brand = "SoleSpec AI"

    def compose_cover_sheet(self, spec: TechPackSpec, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        self._draw_header(c, "SoleSpec AI Technical Pack", spec.model_name)

        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawRightString(
            width - self.margin,
            height - 22 * mm,
            f"Generated: {self._format_timestamp(spec.generated_at)}",
        )
        self._draw_revision_block(c, width - 64 * mm, height - 34 * mm)

        perspective = self._find_render(spec.renders, "perspective")
        self._draw_image(
            c,
            perspective,
            x=22 * mm,
            y=height - 145 * mm,
            box_width=166 * mm,
            box_height=96 * mm,
        )

        self._draw_measurement_summary(
            c,
            spec,
            x=24 * mm,
            y=height - 172 * mm,
            table_width=162 * mm,
        )

        self._draw_section_title(c, "Review Scope", 24 * mm, height - 212 * mm)
        assumptions = [
            "Measurements are derived from normalized geometry and reported in millimeters.",
            "Colorway values are extracted from available material or texture data when present.",
            "Factory teams should confirm dimensions, color standards, and materials before production.",
        ]
        self._draw_bullets(c, assumptions, 28 * mm, height - 226 * mm, max_width=150 * mm)

        self._draw_footer(c)
        c.showPage()
        c.save()

    def compose_measurement_sheet(self, spec: TechPackSpec, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        self._draw_header(c, "Technical Measurements", spec.model_name)

        annotated = self._find_render(spec.annotated_renders, "side_measurements")
        side = self._find_render(spec.renders, "side")
        top = self._find_render(spec.renders, "top")
        front = self._find_render(spec.renders, "front")

        self._draw_image(
            c,
            annotated or side,
            x=18 * mm,
            y=height - 122 * mm,
            box_width=174 * mm,
            box_height=82 * mm,
        )

        self._draw_image(
            c,
            top,
            x=18 * mm,
            y=height - 174 * mm,
            box_width=112 * mm,
            box_height=42 * mm,
        )

        self._draw_image(
            c,
            front,
            x=136 * mm,
            y=height - 174 * mm,
            box_width=56 * mm,
            box_height=42 * mm,
        )

        self._draw_measurement_summary(
            c,
            spec,
            x=26 * mm,
            y=height - 202 * mm,
            table_width=158 * mm,
        )

        self._draw_footer(c)
        c.showPage()
        c.save()

    def compose_technical_drawing_sheet(self, spec: TechPackSpec, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        self._draw_header(c, "2D Technical Drawings", spec.model_name)

        side = self._find_render(spec.annotated_renders, "technical_side")
        top = self._find_render(spec.annotated_renders, "technical_top")
        front = self._find_render(spec.annotated_renders, "technical_front")

        self._draw_image(
            c,
            side,
            x=18 * mm,
            y=height - 128 * mm,
            box_width=174 * mm,
            box_height=88 * mm,
        )

        self._draw_image(
            c,
            top,
            x=18 * mm,
            y=height - 190 * mm,
            box_width=104 * mm,
            box_height=48 * mm,
        )

        self._draw_image(
            c,
            front,
            x=132 * mm,
            y=height - 190 * mm,
            box_width=60 * mm,
            box_height=48 * mm,
        )

        self._draw_section_title(c, "Drawing Scope", 22 * mm, height - 216 * mm)
        notes = [
            "Line-art drawings are generated from normalized Blender render views.",
            "Side drawing includes first-pass length, height, and heel-lift callouts.",
            "Drawings are technical references, not CAD-grade outsole or upper patterns.",
            "Factory teams should verify against source CAD or physical sample standards.",
        ]
        self._draw_bullets(c, notes, 26 * mm, height - 226 * mm, max_width=150 * mm)

        self._draw_footer(c)
        c.showPage()
        c.save()

    def compose_bom_colorway_sheet(self, spec: TechPackSpec, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        self._draw_header(c, "BOM / Colorway Summary", spec.model_name)

        perspective = self._find_render(spec.renders, "perspective")
        self._draw_image(
            c,
            perspective,
            x=18 * mm,
            y=height - 111 * mm,
            box_width=86 * mm,
            box_height=72 * mm,
        )

        y = height - 44 * mm
        self._draw_section_title(c, "Material Colorway", 112 * mm, y)
        y -= 10 * mm

        material_rows = spec.materials or []
        if material_rows:
            for material in material_rows[:3]:
                y = self._draw_material_card(c, material, 112 * mm, y, 76 * mm)
                y -= 6 * mm
        else:
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawString(112 * mm, y, "No material metadata was available.")

        y = height - 128 * mm
        self._draw_table_header(
            c,
            ["Component", "Material", "Confidence"],
            [58 * mm, 75 * mm, 34 * mm],
            18 * mm,
            y,
        )

        y -= 9 * mm
        if spec.components:
            for component in spec.components[:5]:
                material = component.material_name or "Unknown"
                self._draw_table_row(
                    c,
                    [
                        self._friendly_component_name(component.name),
                        material,
                        f"{component.confidence:.2f}",
                    ],
                    [58 * mm, 75 * mm, 34 * mm],
                    18 * mm,
                    y,
                )
                y -= 8 * mm
        else:
            self._draw_table_row(c, ["Whole Shoe Body", "Unknown", "Low"], [58 * mm, 75 * mm, 34 * mm], 18 * mm, y)
            y -= 8 * mm

        self._draw_section_title(c, "Notes", 18 * mm, 86 * mm)
        notes = [
            "Palette values are estimates from GLB material or texture data.",
            "Component extraction remains conservative for monolithic meshes.",
            "Factory should confirm final colors against approved standards.",
        ]
        self._draw_bullets(c, notes, 22 * mm, 76 * mm, max_width=148 * mm)
        self._draw_footer(c)
        c.showPage()
        c.save()

    def compose_validation_report(self, spec: TechPackSpec, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        self._draw_header(c, "Manufacturing Validation Report", spec.model_name)

        perspective = self._find_render(spec.renders, "perspective")
        self._draw_image(
            c,
            perspective,
            x=22 * mm,
            y=height - 92 * mm,
            box_width=166 * mm,
            box_height=52 * mm,
        )

        y = height - 112 * mm
        self._draw_section_title(c, "Validation Findings", 22 * mm, y)
        y -= 10 * mm

        self._draw_table_header(
            c,
            ["Severity", "Category", "Message"],
            [32 * mm, 40 * mm, 96 * mm],
            22 * mm,
            y,
        )
        y -= 9 * mm

        issues = spec.validation_issues or []

        if not issues:
            self._draw_table_row(
                c,
                ["Low", "validation", "No validation concerns were detected by current rules."],
                [32 * mm, 40 * mm, 96 * mm],
                22 * mm,
                y,
            )
            y -= 8 * mm
        else:
            for issue in issues[:8]:
                self._draw_wrapped_validation_row(c, issue, 22 * mm, y)
                y -= 14 * mm

        y -= 8 * mm
        self._draw_section_title(c, "Validation Scope", 22 * mm, y)
        scope_notes = [
            "Rules evaluate global measurements, material metadata, and component extraction confidence.",
            "Findings are decision-support signals, not final production approvals.",
            "Factory teams should verify flagged dimensions and material callouts against physical samples.",
        ]
        self._draw_bullets(c, scope_notes, 26 * mm, y - 10 * mm, max_width=150 * mm)

        method_y = y - 40 * mm
        self._draw_section_title(c, "Method & Assumptions", 22 * mm, method_y)
        self._draw_bullets(
            c,
            self._method_assumptions(spec),
            26 * mm,
            method_y - 10 * mm,
            max_width=150 * mm,
        )

        self._draw_footer(c)
        c.showPage()
        c.save()

    def _draw_revision_block(self, c: canvas.Canvas, x: float, y: float) -> None:
        labels = [("Revision", "A1"), ("Status", "MVP"), ("Units", "mm")]
        table_width = 46 * mm
        row_height = 6 * mm

        c.setStrokeColor(colors.HexColor("#D6D6D6"))
        c.setFillColor(colors.white)
        c.roundRect(x, y - len(labels) * row_height, table_width, len(labels) * row_height, 1.5 * mm, fill=1, stroke=1)

        current_y = y - 4.5 * mm
        for index, (label, value) in enumerate(labels):
            if index:
                c.setStrokeColor(colors.HexColor("#ECECEC"))
                c.line(x, current_y + 2.5 * mm, x + table_width, current_y + 2.5 * mm)
            c.setFont("Helvetica", 7.5)
            c.setFillColor(colors.HexColor("#666666"))
            c.drawString(x + 3 * mm, current_y, label)
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColor(colors.HexColor("#111111"))
            c.drawRightString(x + table_width - 3 * mm, current_y, value)
            current_y -= row_height

    def _draw_header(self, c: canvas.Canvas, title: str, model_name: str) -> None:
        width, height = A4
        c.setFillColor(colors.HexColor("#111111"))
        c.setFont("Helvetica-Bold", 20)
        c.drawString(self.margin, height - 20 * mm, title)

        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(self.margin, height - 29 * mm, f"Model: {model_name}")

        c.setStrokeColor(colors.HexColor("#D9D9D9"))
        c.setLineWidth(0.8)
        c.line(self.margin, height - 35 * mm, width - self.margin, height - 35 * mm)

    def _draw_footer(self, c: canvas.Canvas) -> None:
        width, _ = A4
        c.setStrokeColor(colors.HexColor("#D9D9D9"))
        c.setLineWidth(0.6)
        c.line(self.margin, 18 * mm, width - self.margin, 18 * mm)

        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#777777"))
        c.drawString(self.margin, 11 * mm, f"Generated by {self.brand}")
        c.drawRightString(width - self.margin, 11 * mm, "Factory-facing technical reference")

    def _draw_image(
        self,
        c: canvas.Canvas,
        render: RenderSpec | None,
        x: float,
        y: float,
        box_width: float,
        box_height: float,
    ) -> None:
        c.setFillColor(colors.HexColor("#F7F7F5"))
        c.roundRect(x, y, box_width, box_height, 3 * mm, fill=1, stroke=0)

        if render is None or not Path(render.image_path).exists():
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#777777"))
            c.drawCentredString(x + box_width / 2, y + box_height / 2, "Render unavailable")
            return

        image_source = self._prepare_pdf_image(render.image_path)
        c.drawImage(
            image_source,
            x + 3 * mm,
            y + 3 * mm,
            width=box_width - 6 * mm,
            height=box_height - 6 * mm,
            preserveAspectRatio=True,
            anchor="c",
        )

    def _draw_measurement_summary(
        self,
        c: canvas.Canvas,
        spec: TechPackSpec,
        x: float,
        y: float,
        table_width: float,
    ) -> None:
        rows = [
            ("Length", spec.measurements.length_mm),
            ("Width", spec.measurements.width_mm),
            ("Height", spec.measurements.height_mm),
            ("Heel Height", spec.measurements.heel_height_mm),
            ("Sole Thickness", spec.measurements.sole_thickness_mm),
        ]

        row_height = 8 * mm
        c.setStrokeColor(colors.HexColor("#D6D6D6"))
        c.setFillColor(colors.white)
        c.roundRect(x, y - (len(rows) * row_height), table_width, len(rows) * row_height, 2 * mm, fill=1, stroke=1)

        current_y = y - 6 * mm
        for index, (label, value) in enumerate(rows):
            if index:
                c.setStrokeColor(colors.HexColor("#EAEAEA"))
                c.line(x, current_y + 3 * mm, x + table_width, current_y + 3 * mm)

            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#555555"))
            c.drawString(x + 5 * mm, current_y, label)

            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#111111"))
            value_text = f"{value:.0f} mm" if value is not None else "Unavailable"
            c.drawRightString(x + table_width - 5 * mm, current_y, value_text)
            current_y -= row_height

    def _draw_pipeline_notes(self, c: canvas.Canvas, y: float) -> None:
        self._draw_section_title(c, "Pipeline Notes", 24 * mm, y)
        notes = [
            "Orientation normalized into canonical footwear coordinates.",
            "Scale normalization applied to match plausible footwear dimensions.",
            "Render views generated using a Blender-based glTF renderer.",
            "Measurements derived from transformed scene geometry.",
        ]
        self._draw_bullets(c, notes, 28 * mm, y - 10 * mm, max_width=150 * mm)

    def _draw_confidence_scores(self, c: canvas.Canvas, x: float, y: float) -> None:
        self._draw_section_title(c, "Extraction Confidence", x, y + 25 * mm)
        self._draw_table_header(
            c,
            ["Capability", "Confidence"],
            [92 * mm, 48 * mm],
            x,
            y + 14 * mm,
        )
        rows = [
            ("Global Measurements", "High"),
            ("Material Extraction", "Medium"),
            ("Component Segmentation", "Low"),
        ]
        current_y = y + 5 * mm
        for row in rows:
            self._draw_table_row(c, list(row), [92 * mm, 48 * mm], x, current_y)
            current_y -= 8 * mm

    def _draw_section_title(self, c: canvas.Canvas, title: str, x: float, y: float) -> None:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#111111"))
        c.drawString(x, y, title)

    def _draw_bullets(self, c: canvas.Canvas, bullets: list[str], x: float, y: float, max_width: float) -> None:
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#333333"))
        current_y = y
        for bullet in bullets:
            lines = self._wrap_text(c, bullet, max_width - 6 * mm)
            for index, line in enumerate(lines):
                prefix = "- " if index == 0 else "  "
                c.drawString(x, current_y, f"{prefix}{line}")
                current_y -= 5 * mm
            current_y -= 1 * mm

    def _draw_table_header(
        self,
        c: canvas.Canvas,
        labels: list[str],
        widths: list[float],
        x: float,
        y: float,
    ) -> None:
        c.setFillColor(colors.HexColor("#111111"))
        c.roundRect(x, y - 6 * mm, sum(widths), 8 * mm, 1.5 * mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.white)

        current_x = x + 3 * mm
        for label, column_width in zip(labels, widths):
            c.drawString(current_x, y - 3.5 * mm, label)
            current_x += column_width

    def _draw_table_row(
        self,
        c: canvas.Canvas,
        values: list[str],
        widths: list[float],
        x: float,
        y: float,
    ) -> None:
        c.setStrokeColor(colors.HexColor("#E2E2E2"))
        c.line(x, y - 2.5 * mm, x + sum(widths), y - 2.5 * mm)
        c.setFont("Helvetica", 8.5)
        c.setFillColor(colors.HexColor("#222222"))

        current_x = x + 3 * mm
        for value, column_width in zip(values, widths):
            c.drawString(current_x, y, str(value)[:42])
            current_x += column_width

    def _draw_wrapped_validation_row(self, c: canvas.Canvas, issue, x: float, y: float) -> None:
        severity = issue.get("severity", "low") if isinstance(issue, dict) else issue.severity
        category = issue.get("category", "general") if isinstance(issue, dict) else issue.category
        message = issue.get("message", "") if isinstance(issue, dict) else issue.message

        widths = [32 * mm, 40 * mm, 96 * mm]
        c.setStrokeColor(colors.HexColor("#E2E2E2"))
        c.line(x, y - 2.5 * mm, x + sum(widths), y - 2.5 * mm)

        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(self._severity_color(severity))
        c.drawString(x + 3 * mm, y, severity.title())

        c.setFont("Helvetica", 8.5)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(x + widths[0] + 3 * mm, y, category.title())

        lines = self._wrap_text(c, message, widths[2] - 6 * mm)
        message_x = x + widths[0] + widths[1] + 3 * mm
        current_y = y
        for line in lines[:2]:
            c.drawString(message_x, current_y, line)
            current_y -= 4.5 * mm

    def _find_render(self, renders: list[RenderSpec], view_name: str) -> RenderSpec | None:
        for render in renders:
            if render.view_name == view_name:
                return render

        return None

    def _prepare_pdf_image(self, image_path: str):
        path = Path(image_path)
        try:
            image = Image.open(path).convert("RGB")
            cropped = self._crop_render_background(image)
        except Exception:
            return str(path)

        buffer = BytesIO()
        cropped.save(buffer, format="PNG")
        buffer.seek(0)
        return ImageReader(buffer)

    def _crop_render_background(self, image: Image.Image) -> Image.Image:
        gray = image.convert("L")
        width, height = image.size
        pixels = gray.load()

        threshold = 82
        xs: list[int] = []
        ys: list[int] = []

        step = max(1, min(width, height) // 600)
        for y in range(0, height, step):
            for x in range(0, width, step):
                if pixels[x, y] > threshold:
                    xs.append(x)
                    ys.append(y)

        if not xs or not ys:
            return image

        left = max(0, min(xs) - 36)
        right = min(width, max(xs) + 36)
        top = max(0, min(ys) - 36)
        bottom = min(height, max(ys) + 36)

        if (right - left) < width * 0.2 or (bottom - top) < height * 0.35:
            return image

        return image.crop((left, top, right, bottom))

    def _friendly_component_name(self, name: str) -> str:
        if name == "unknown_component":
            return "Whole Shoe Body"

        return name.replace("_", " ").title()

    def _severity_color(self, severity: str):
        if severity == "high":
            return colors.HexColor("#A40000")
        if severity == "medium":
            return colors.HexColor("#B45F00")
        return colors.HexColor("#4D6A1F")

    def _draw_material_card(self, c: canvas.Canvas, material, x: float, y: float, width: float) -> float:
        card_height = 35 * mm
        c.setFillColor(colors.HexColor("#FAFAF8"))
        c.setStrokeColor(colors.HexColor("#E0E0DC"))
        c.roundRect(x, y - card_height, width, card_height, 2 * mm, fill=1, stroke=1)

        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(colors.HexColor("#111111"))
        c.drawString(x + 4 * mm, y - 7 * mm, str(material.name)[:32])

        c.setFont("Helvetica", 7.5)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(x + 4 * mm, y - 13 * mm, f"Type: {material.inferred_type or 'unknown'}")
        c.drawString(x + 4 * mm, y - 18 * mm, f"RGB: {self._format_rgb(material.base_color_rgb)}")
        c.drawString(x + 4 * mm, y - 23 * mm, f"Confidence: {material.confidence:.2f}")

        if material.base_color_rgb:
            self._draw_color_swatch(c, material.base_color_rgb, x + width - 17 * mm, y - 15 * mm, 11 * mm)

        palette = material.dominant_colors_rgb[:5]
        if palette:
            swatch_x = x + 4 * mm
            swatch_y = y - 31 * mm
            for palette_color in palette:
                self._draw_color_swatch(c, palette_color, swatch_x, swatch_y, 5 * mm)
                swatch_x += 7 * mm

        return y - card_height

    def _draw_color_swatch(self, c: canvas.Canvas, rgb: list[int], x: float, y: float, size: float) -> None:
        c.setFillColor(colors.Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255))
        c.setStrokeColor(colors.HexColor("#777777"))
        c.roundRect(x, y, size, size, 0.8 * mm, fill=1, stroke=1)

    def _format_rgb(self, rgb: list[int] | None) -> str:
        if not rgb:
            return "Not available"

        return f"{rgb[0]}, {rgb[1]}, {rgb[2]}"

    def _method_assumptions(self, spec: TechPackSpec) -> list[str]:
        metadata = spec.normalization_metadata or {}
        scale_applied = metadata.get("scale_applied")
        original_length = metadata.get("original_length_mm_assuming_meters")
        target_length = metadata.get("target_length_mm")

        notes = [
            "GLB units are treated as meters and sanity-checked against footwear dimensions.",
            "Geometry is normalized so X=length, Y=height, and Z=width before measurement.",
            "Component extraction is heuristic; monolithic meshes are reported conservatively.",
            "Measurements and renders use an exported normalized intermediate GLB.",
        ]

        if scale_applied is not None:
            scale_text = "applied" if scale_applied else "not applied"
            notes.append(
                f"Scale normalization {scale_text}; original length estimate {original_length} mm, target {target_length} mm."
            )

        return notes

    def _format_timestamp(self, timestamp: str) -> str:
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return timestamp

        return parsed.strftime("%Y-%m-%d %H:%M UTC")

    def _wrap_text(self, c: canvas.Canvas, text: str, max_width: float) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""

        for word in words:
            candidate = f"{current} {word}".strip()
            if c.stringWidth(candidate, "Helvetica", 9) <= max_width:
                current = candidate
                continue

            if current:
                lines.append(current)
            current = word

        if current:
            lines.append(current)

        return lines
