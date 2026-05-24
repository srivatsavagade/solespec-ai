from src.solespec.schemas.techpack_schema import (
    ComponentSpec,
    MaterialSpec,
    MeasurementSpec,
)
from src.solespec.validation.rules import (
    validate_components,
    validate_materials,
    validate_measurements,
)
from src.solespec.validation.validation_schema import ValidationIssue


class ValidationEngine:
    def validate(
        self,
        measurements: MeasurementSpec,
        components: list[ComponentSpec],
        materials: list[MaterialSpec],
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        issues.extend(validate_measurements(measurements))
        issues.extend(validate_components(components))
        issues.extend(validate_materials(materials))

        return sorted(
            issues,
            key=lambda issue: self._severity_rank(issue.severity),
            reverse=True,
        )

    def _severity_rank(self, severity: str) -> int:
        return {
            "high": 3,
            "medium": 2,
            "low": 1,
        }.get(severity, 0)
