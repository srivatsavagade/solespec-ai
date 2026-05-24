from datetime import datetime, timezone
from pathlib import Path

from src.solespec.agentic.state import TechPackState
from src.solespec.manufacturing_ai.confidence_scorer import ConfidenceScorer
from src.solespec.manufacturing_ai.knowledge_retriever import (
    ManufacturingKnowledgeRetriever,
)
from src.solespec.manufacturing_ai.notes_generator import ManufacturingNotesGenerator
from src.solespec.schemas.techpack_schema import TechPackSpec


def notes_node(state: TechPackState) -> TechPackState:
    input_path = Path(state["input_path"])

    spec = TechPackSpec(
        model_name=input_path.stem,
        generated_at=datetime.now(timezone.utc).isoformat(),
        seed=int(state.get("seed", 42)),
        measurements=state["measurements"],
        components=state["components"],
        materials=state["materials"],
        renders=state["renders"],
        normalization_metadata=state.get("scale_metadata", {}),
        annotated_renders=state.get("annotated_renders", []),
        validation_issues=[
            issue.to_dict() for issue in state.get("validation_issues", [])
        ],
    )

    spec.manufacturing_evidence = ManufacturingKnowledgeRetriever().retrieve_for_spec(spec)
    spec.confidence_scores = ConfidenceScorer().score(spec)
    spec.manufacturing_notes = ManufacturingNotesGenerator().generate(spec)
    spec.manufacturing_notes.extend(state.get("review_notes", []))

    return {
        **state,
        "notes": spec.manufacturing_notes,
        "manufacturing_evidence": spec.manufacturing_evidence,
        "confidence_scores": spec.confidence_scores,
        "spec": spec,
    }
