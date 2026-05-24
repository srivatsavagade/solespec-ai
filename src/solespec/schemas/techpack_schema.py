from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class MeasurementSpec:
    length_mm: float | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    heel_height_mm: float | None = None
    sole_thickness_mm: float | None = None


@dataclass
class ComponentSpec:
    name: str
    mesh_name: str
    bbox_mm: dict[str, float]
    material_name: str | None = None
    confidence: float = 0.5
    notes: str | None = None


@dataclass
class MaterialSpec:
    name: str
    base_color_rgb: list[int] | None = None
    base_color_hex: str | None = None
    dominant_colors_rgb: list[list[int]] = field(default_factory=list)
    dominant_colors_hex: list[str] = field(default_factory=list)
    color_source: str = "unavailable"
    color_standard_note: str = "Pantone/RAL mapping not implemented; factory should confirm approved color standard."
    inferred_type: str | None = None
    confidence: float = 0.5


@dataclass
class RenderSpec:
    view_name: str
    image_path: str


@dataclass
class ConfidenceSpec:
    geometry: float
    material: float
    component: float
    factory_readiness: float
    rationale: list[str] = field(default_factory=list)


@dataclass
class TechPackSpec:
    model_name: str
    generated_at: str
    seed: int
    measurements: MeasurementSpec
    components: list[ComponentSpec]
    materials: list[MaterialSpec]
    renders: list[RenderSpec]
    normalization_metadata: dict[str, Any] = field(default_factory=dict)
    confidence_scores: ConfidenceSpec | None = None
    manufacturing_evidence: list[dict[str, Any]] = field(default_factory=list)
    run_manifest: dict[str, Any] = field(default_factory=dict)
    annotated_renders: list[RenderSpec] = field(default_factory=list)
    validation_issues: list[Any] = field(default_factory=list)
    manufacturing_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
