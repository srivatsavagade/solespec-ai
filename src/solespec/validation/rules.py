from src.solespec.schemas.techpack_schema import (
    ComponentSpec,
    MaterialSpec,
    MeasurementSpec,
)
from src.solespec.validation.validation_schema import ValidationIssue


def validate_measurements(measurements: MeasurementSpec) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if measurements.length_mm is not None:
        if measurements.length_mm < 180 or measurements.length_mm > 380:
            issues.append(
                ValidationIssue(
                    severity="high",
                    category="geometry",
                    message="Shoe length is outside expected manufacturing range.",
                )
            )

    if measurements.width_mm is not None:
        if measurements.width_mm > 140:
            issues.append(
                ValidationIssue(
                    severity="medium",
                    category="geometry",
                    message="Shoe width is outside expected manufacturing range.",
                )
            )
        elif measurements.width_mm < 70:
            issues.append(
                ValidationIssue(
                    severity="medium",
                    category="geometry",
                    message="Shoe width is unusually narrow for standard footwear production.",
                )
            )

    if measurements.heel_height_mm is not None and measurements.heel_height_mm > 80:
        issues.append(
            ValidationIssue(
                severity="medium",
                category="geometry",
                message="Heel height exceeds common athletic footwear thresholds.",
            )
        )

    if measurements.sole_thickness_mm is not None:
        if measurements.sole_thickness_mm < 15:
            issues.append(
                ValidationIssue(
                    severity="low",
                    category="construction",
                    message="Sole thickness estimate is slim; confirm outsole and midsole construction requirements.",
                )
            )
        elif measurements.sole_thickness_mm > 60:
            issues.append(
                ValidationIssue(
                    severity="medium",
                    category="construction",
                    message="Sole thickness estimate is unusually high and should be factory-verified.",
                )
            )

    return issues


def validate_components(components: list[ComponentSpec]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not components:
        return [
            ValidationIssue(
                severity="medium",
                category="segmentation",
                message="No component meshes were extracted from the source asset.",
            )
        ]

    if len(components) == 1 and components[0].name == "unknown_component":
        issues.append(
            ValidationIssue(
                severity="low",
                category="segmentation",
                message="Input asset was monolithic and lacked semantic segmentation metadata.",
            )
        )

    for component in components:
        if component.confidence < 0.5:
            issues.append(
                ValidationIssue(
                    severity="medium",
                    category="segmentation",
                    message=f"Component extraction confidence is low for {component.mesh_name}.",
                )
            )

    return issues


def validate_materials(materials: list[MaterialSpec]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not materials:
        return [
            ValidationIssue(
                severity="medium",
                category="material",
                message="No material metadata was available from the source asset.",
            )
        ]

    for material in materials:
        if material.base_color_rgb is None:
            issues.append(
                ValidationIssue(
                    severity="medium",
                    category="material",
                    message=f"Material color metadata unavailable for {material.name}.",
                )
            )

        if material.confidence < 0.5:
            issues.append(
                ValidationIssue(
                    severity="low",
                    category="material",
                    message=f"Material inference confidence is low for {material.name}.",
                )
            )

    return issues
