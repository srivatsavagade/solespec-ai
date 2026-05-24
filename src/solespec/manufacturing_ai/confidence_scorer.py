from statistics import mean

from src.solespec.schemas.techpack_schema import ConfidenceSpec, TechPackSpec


class ConfidenceScorer:
    def score(self, spec: TechPackSpec) -> ConfidenceSpec:
        rationale: list[str] = []

        geometry = self._score_geometry(spec, rationale)
        material = self._score_materials(spec, rationale)
        component = self._score_components(spec, rationale)

        issue_penalty = self._issue_penalty(spec)
        factory_readiness = max(0.0, mean([geometry, material, component]) - issue_penalty)

        if issue_penalty:
            rationale.append(
                f"Factory readiness reduced by {issue_penalty:.2f} due to medium/high validation findings."
            )

        return ConfidenceSpec(
            geometry=round(geometry, 2),
            material=round(material, 2),
            component=round(component, 2),
            factory_readiness=round(factory_readiness, 2),
            rationale=rationale,
        )

    def _score_geometry(self, spec: TechPackSpec, rationale: list[str]) -> float:
        required = [
            spec.measurements.length_mm,
            spec.measurements.width_mm,
            spec.measurements.height_mm,
            spec.measurements.heel_height_mm,
            spec.measurements.sole_thickness_mm,
        ]
        available_ratio = sum(value is not None for value in required) / len(required)
        score = 0.55 + available_ratio * 0.35

        if spec.normalization_metadata.get("scale_applied"):
            score -= 0.08
            rationale.append("Geometry confidence reduced because scale normalization was required.")

        return max(0.0, min(1.0, score))

    def _score_materials(self, spec: TechPackSpec, rationale: list[str]) -> float:
        if not spec.materials:
            rationale.append("Material confidence low because no material metadata was available.")
            return 0.2

        values = [material.confidence for material in spec.materials]
        score = mean(values)
        if any(material.color_source == "unavailable" for material in spec.materials):
            score -= 0.15
            rationale.append("Material confidence reduced because some colors were unavailable.")

        return max(0.0, min(1.0, score))

    def _score_components(self, spec: TechPackSpec, rationale: list[str]) -> float:
        if not spec.components:
            rationale.append("Component confidence low because no components were extracted.")
            return 0.15

        score = mean(component.confidence for component in spec.components)
        if all(component.name == "unknown_component" for component in spec.components):
            score -= 0.25
            rationale.append("Component confidence reduced because the asset appears monolithic.")

        return max(0.0, min(1.0, score))

    def _issue_penalty(self, spec: TechPackSpec) -> float:
        penalty = 0.0
        for issue in spec.validation_issues:
            if not isinstance(issue, dict):
                continue
            if issue.get("severity") == "high":
                penalty += 0.15
            elif issue.get("severity") == "medium":
                penalty += 0.08

        return min(0.35, penalty)
