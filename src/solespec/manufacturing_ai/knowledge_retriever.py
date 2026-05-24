from dataclasses import dataclass
from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.solespec.schemas.techpack_schema import TechPackSpec


@dataclass
class EvidenceChunk:
    rule_id: str
    title: str
    text: str
    score: float

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "text": self.text,
            "score": round(float(self.score), 4),
        }


class ManufacturingKnowledgeRetriever:
    def __init__(self, knowledge_path: Path | None = None):
        self.knowledge_path = knowledge_path or Path("docs/manufacturing_guidelines.md")

    def retrieve_for_spec(self, spec: TechPackSpec, top_k: int = 5) -> list[dict]:
        chunks = self._load_chunks()
        if not chunks:
            return []

        query = self._build_query(spec)
        documents = [chunk.text for chunk in chunks]
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(documents + [query])
        scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

        ranked = sorted(
            [
                EvidenceChunk(
                    rule_id=chunk.rule_id,
                    title=chunk.title,
                    text=chunk.text,
                    score=float(scores[index]),
                )
                for index, chunk in enumerate(chunks)
            ],
            key=lambda chunk: chunk.score,
            reverse=True,
        )

        return [chunk.to_dict() for chunk in ranked[:top_k] if chunk.score > 0]

    def _load_chunks(self) -> list[EvidenceChunk]:
        if not self.knowledge_path.exists():
            return []

        content = self.knowledge_path.read_text(encoding="utf-8")
        sections = re.split(r"(?m)^##\s+", content)
        chunks: list[EvidenceChunk] = []

        for section in sections:
            section = section.strip()
            if not section or section.startswith("#"):
                continue

            lines = section.splitlines()
            title = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            match = re.match(r"\[(?P<id>[A-Z0-9_-]+)\]\s*(?P<title>.*)", title)
            rule_id = match.group("id") if match else title.lower().replace(" ", "_")
            clean_title = match.group("title") if match else title
            chunks.append(
                EvidenceChunk(
                    rule_id=rule_id,
                    title=clean_title,
                    text=body,
                    score=0.0,
                )
            )

        return chunks

    def _build_query(self, spec: TechPackSpec) -> str:
        issues = [
            issue.get("message", "")
            for issue in spec.validation_issues
            if isinstance(issue, dict)
        ]
        materials = [
            f"{material.name} {material.inferred_type} {material.color_source}"
            for material in spec.materials
        ]
        components = [
            f"{component.name} {component.notes or ''}"
            for component in spec.components
        ]
        measurements = spec.measurements

        return " ".join(
            [
                f"length {measurements.length_mm} width {measurements.width_mm}",
                f"height {measurements.height_mm} heel {measurements.heel_height_mm}",
                f"sole thickness {measurements.sole_thickness_mm}",
                " ".join(issues),
                " ".join(materials),
                " ".join(components),
            ]
        )
