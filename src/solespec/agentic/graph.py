from langgraph.graph import END, StateGraph

from src.solespec.agentic.nodes.geometry_node import geometry_node
from src.solespec.agentic.nodes.ingestion_node import ingestion_node
from src.solespec.agentic.nodes.manufacturing_review_node import (
    manufacturing_review_node,
)
from src.solespec.agentic.nodes.notes_node import notes_node
from src.solespec.agentic.nodes.normalization_node import normalization_node
from src.solespec.agentic.nodes.pdf_node import pdf_node
from src.solespec.agentic.nodes.rendering_node import rendering_node
from src.solespec.agentic.nodes.validation_node import validation_node
from src.solespec.agentic.state import TechPackState


def build_graph():
    graph = StateGraph(TechPackState)

    graph.add_node("ingestion", ingestion_node)
    graph.add_node("normalization", normalization_node)
    graph.add_node("geometry", geometry_node)
    graph.add_node("validation", validation_node)
    graph.add_node("rendering", rendering_node)
    graph.add_node("notes", notes_node)
    graph.add_node("manufacturing_review", manufacturing_review_node)
    graph.add_node("pdf", pdf_node)

    graph.set_entry_point("ingestion")

    graph.add_edge("ingestion", "normalization")
    graph.add_edge("normalization", "geometry")
    graph.add_edge("geometry", "validation")
    graph.add_edge("validation", "rendering")
    graph.add_edge("rendering", "notes")
    graph.add_edge("notes", "manufacturing_review")
    graph.add_edge("manufacturing_review", "pdf")
    graph.add_edge("pdf", END)

    return graph.compile()
