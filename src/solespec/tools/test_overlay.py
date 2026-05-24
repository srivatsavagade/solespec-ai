import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(PROJECT_ROOT))


from src.solespec.document_engine.overlay_generator import OverlayGenerator
from src.solespec.schemas.techpack_schema import MeasurementSpec


spec_path = PROJECT_ROOT / "outputs" / "schemas" / "techpack_spec.json"

with spec_path.open("r", encoding="utf-8") as f:
    spec = json.load(f)

measurements = MeasurementSpec(**spec["measurements"])

OverlayGenerator().generate_measurement_overlay(
    image_path=PROJECT_ROOT / "outputs" / "renders" / "side.png",
    output_path=PROJECT_ROOT / "outputs" / "annotated" / "side_overlay_test.png",
    measurements=measurements,
)
