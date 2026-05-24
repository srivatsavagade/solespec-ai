from typing import Any, TypedDict


class TechPackState(TypedDict, total=False):
    input_path: str
    output_dir: str
    seed: int
    review_overrides_path: str
    scene: Any
    scale_metadata: dict[str, Any]
    measurements: Any
    components: Any
    materials: Any
    validation_issues: Any
    renders: Any
    annotated_renders: Any
    review_notes: list[str]
    notes: Any
    manufacturing_review: list[str]
    manufacturing_evidence: list[dict[str, Any]]
    confidence_scores: Any
    spec: Any
    pdf_paths: list[str]
