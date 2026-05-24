from src.solespec.agentic.state import TechPackState
from src.solespec.validation.validation_engine import ValidationEngine


def validation_node(state: TechPackState) -> TechPackState:
    validation_issues = ValidationEngine().validate(
        measurements=state["measurements"],
        components=state["components"],
        materials=state["materials"],
    )

    return {
        **state,
        "validation_issues": validation_issues,
    }
