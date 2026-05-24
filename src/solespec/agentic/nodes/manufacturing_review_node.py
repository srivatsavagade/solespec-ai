from src.solespec.agentic.state import TechPackState


def manufacturing_review_node(state: TechPackState) -> TechPackState:
    measurements = state["measurements"]
    materials = state.get("materials", [])
    components = state.get("components", [])
    validation_issues = state.get("validation_issues", [])
    has_color = materials and any(material.base_color_rgb is not None for material in materials)

    review: list[str] = [
        "QA should verify normalized dimensions against a physical reference sample before production release.",
    ]

    if has_color:
        review.append(
            "Colorway values were estimated from available GLB material or texture data; factory should confirm against approved color standards."
        )
    else:
        review.append(
            "Factory should confirm material callouts because the source GLB did not expose reliable color metadata."
        )

    high_or_medium = [
        issue for issue in validation_issues
        if issue.severity in {"high", "medium"}
    ]
    if high_or_medium:
        review.append(
            f"Validation engine flagged {len(high_or_medium)} medium/high manufacturing concern(s)."
        )

    if components and all(component.name == "unknown_component" for component in components):
        review.append(
            "Component segmentation confidence is low because the source asset is monolithic."
        )

    if measurements.sole_thickness_mm is not None and measurements.sole_thickness_mm < 15:
        review.append(
            "Sole thickness estimate is slim; confirm outsole and midsole construction requirements."
        )

    if not has_color:
        review.append(
            "Colorway extraction is incomplete; request Pantone/RGB approval from design before factory handoff."
        )

    evidence = state.get("manufacturing_evidence", [])
    if evidence:
        rule_ids = ", ".join(item["rule_id"] for item in evidence[:3])
        review.append(
            f"Manufacturing review grounded against retrieved guideline(s): {rule_ids}."
        )

    confidence_scores = state.get("confidence_scores")
    if confidence_scores is not None:
        review.append(
            f"Factory readiness confidence score: {confidence_scores.factory_readiness:.2f}."
        )

    spec = state["spec"]
    spec.manufacturing_notes.extend(review)

    return {
        **state,
        "manufacturing_review": review,
        "spec": spec,
    }
