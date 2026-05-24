import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[3]


ASSETS = [
    {
        "label": "Original / New Balance",
        "output_dir": PROJECT_ROOT / "outputs",
        "summary": "Heel, material, segmentation warnings",
    },
    {
        "label": "Flower Sneaker",
        "output_dir": PROJECT_ROOT / "outputs_flower_sneakers_shoe_scan",
        "summary": "Heel-height + thin-sole warnings",
    },
    {
        "label": "Miles Morales Shoe",
        "output_dir": PROJECT_ROOT / "outputs_miles_morales_shoes",
        "summary": "Material metadata + segmentation warnings",
    },
]


def load_font(name: str, size: int):
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def load_spec(output_dir: Path) -> dict:
    spec_path = output_dir / "schemas" / "techpack_spec.json"
    with spec_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    max_width: int,
    line_height: int,
) -> int:
    x, y = xy
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word

    if current:
        lines.append(current)

    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height

    return y


def main() -> None:
    output_path = PROJECT_ROOT / "outputs" / "comparison_collage.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width = 1800
    row_height = 420
    header_height = 150
    height = header_height + row_height * len(ASSETS) + 70

    image = Image.new("RGB", (width, height), (248, 248, 246))
    draw = ImageDraw.Draw(image)

    title_font = load_font("arialbd.ttf", 48)
    header_font = load_font("arialbd.ttf", 28)
    body_font = load_font("arial.ttf", 24)
    small_font = load_font("arial.ttf", 21)

    draw.text((60, 42), "SoleSpec AI Multi-Asset Validation", font=title_font, fill=(18, 18, 18))
    draw.text(
        (60, 100),
        "Input-dependent manufacturing concerns across three GLB footwear assets",
        font=body_font,
        fill=(80, 80, 80),
    )

    columns = {
        "asset": 60,
        "render": 420,
        "summary": 1120,
    }

    y = header_height
    draw.rectangle((40, y - 18, width - 40, y + 30), fill=(22, 22, 22))
    draw.text((columns["asset"], y - 8), "Asset", font=header_font, fill=(255, 255, 255))
    draw.text((columns["render"], y - 8), "Perspective Render", font=header_font, fill=(255, 255, 255))
    draw.text((columns["summary"], y - 8), "Validation Summary", font=header_font, fill=(255, 255, 255))

    y += 54

    for index, asset in enumerate(ASSETS):
        row_top = y + index * row_height
        row_bottom = row_top + row_height - 24

        draw.rounded_rectangle(
            (40, row_top, width - 40, row_bottom),
            radius=12,
            fill=(255, 255, 255),
            outline=(220, 220, 220),
            width=2,
        )

        spec = load_spec(asset["output_dir"])
        render_path = asset["output_dir"] / "renders" / "perspective.png"
        render = Image.open(render_path).convert("RGB")
        render.thumbnail((610, 330), Image.Resampling.LANCZOS)

        render_x = columns["render"]
        render_y = row_top + 42
        draw.rounded_rectangle(
            (render_x - 16, render_y - 16, render_x + 630, render_y + 350),
            radius=10,
            fill=(247, 247, 245),
        )
        image.paste(render, (render_x + (610 - render.width) // 2, render_y + (330 - render.height) // 2))

        draw.text((columns["asset"], row_top + 48), asset["label"], font=header_font, fill=(22, 22, 22))
        draw.text(
            (columns["asset"], row_top + 94),
            f"Model: {spec['model_name']}",
            font=small_font,
            fill=(90, 90, 90),
        )

        m = spec["measurements"]
        measurement_text = (
            f"L {m['length_mm']:.0f} mm | W {m['width_mm']:.0f} mm | "
            f"H {m['height_mm']:.0f} mm"
        )
        draw.text((columns["asset"], row_top + 132), measurement_text, font=small_font, fill=(90, 90, 90))

        draw.text((columns["summary"], row_top + 48), asset["summary"], font=header_font, fill=(22, 22, 22))

        issues = spec.get("validation_issues", [])
        issue_y = row_top + 104
        for issue in issues[:4]:
            severity = issue["severity"].title()
            category = issue["category"].title()
            message = issue["message"]
            color = (170, 86, 0) if issue["severity"] == "medium" else (75, 105, 35)
            draw.text((columns["summary"], issue_y), f"{severity} / {category}", font=small_font, fill=color)
            issue_y = draw_wrapped_text(
                draw=draw,
                text=message,
                xy=(columns["summary"], issue_y + 30),
                font=small_font,
                fill=(70, 70, 70),
                max_width=600,
                line_height=27,
            )
            issue_y += 10

    draw.text(
        (60, height - 45),
        "Generated by SoleSpec AI - deterministic extraction, validation intelligence, bounded LangGraph orchestration",
        font=small_font,
        fill=(105, 105, 105),
    )

    image.save(output_path)
    print(f"Saved comparison collage: {output_path}")


if __name__ == "__main__":
    main()
