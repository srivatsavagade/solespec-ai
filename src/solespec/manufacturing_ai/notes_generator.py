from src.solespec.schemas.techpack_schema import TechPackSpec


class ManufacturingNotesGenerator:
    def generate(self, spec: TechPackSpec) -> list[str]:
        # MVP deterministic fallback.
        # Later we can replace this with constrained LLM generation from spec.to_dict().
        notes = [
            "Verify all measurements against physical production sample before mass manufacturing.",
            "Use extracted component and material table as the primary BOM reference.",
            "Maintain consistent color matching across upper, sole, and accessory components.",
            "Inspect stitching, bonding, and edge finishing during QA.",
        ]

        if spec.components:
            component_names = sorted({c.name for c in spec.components})
            notes.append(f"Detected components for factory review: {', '.join(component_names)}.")

        if spec.manufacturing_evidence:
            evidence_ids = ", ".join(
                evidence["rule_id"]
                for evidence in spec.manufacturing_evidence[:3]
            )
            notes.append(
                f"Review notes are grounded in retrieved manufacturing guidelines: {evidence_ids}."
            )

        if spec.confidence_scores is not None:
            notes.append(
                f"Factory readiness confidence score: {spec.confidence_scores.factory_readiness:.2f}."
            )

        return notes
