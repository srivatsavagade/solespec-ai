from datetime import datetime, timezone
from pathlib import Path
import random
import numpy as np

from src.solespec.ingestion.glb_loader import GLBLoader
from src.solespec.normalization.scene_normalizer import SceneNormalizer
from src.solespec.geometry_engine.geometry_analyzer import GeometryAnalyzer
from src.solespec.material_engine.material_analyzer import MaterialAnalyzer
from src.solespec.manufacturing_ai.confidence_scorer import ConfidenceScorer
from src.solespec.manufacturing_ai.knowledge_retriever import (
    ManufacturingKnowledgeRetriever,
)
from src.solespec.manufacturing_ai.notes_generator import ManufacturingNotesGenerator
from src.solespec.document_engine.pdf_composer import PDFComposer
from src.solespec.document_engine.overlay_generator import OverlayGenerator
from src.solespec.document_engine.technical_drawing_generator import (
    TechnicalDrawingGenerator,
)
from src.solespec.schemas.techpack_schema import TechPackSpec
from src.solespec.utils.json_io import save_json
from src.solespec.utils.run_manifest import build_run_manifest
from src.solespec.utils.scene_export import export_scene_glb
from src.solespec.rendering_engine.blender_renderer import BlenderRenderer
from src.solespec.review.overrides import (
    apply_review_overrides,
    load_review_overrides,
)
from src.solespec.geometry_engine.footwear_measurements import (
    FootwearMeasurementEngine
)
from src.solespec.normalization.scale_normalizer import ScaleNormalizer
from src.solespec.validation.validation_engine import ValidationEngine


class TechPackPipeline:
    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        seed: int = 42,
        review_overrides_path: Path | None = None,
    ):
        self.input_path = input_path
        self.output_dir = output_dir
        self.seed = seed
        self.review_overrides_path = review_overrides_path

    def run(self) -> TechPackSpec:
        self._set_seed()

        scene = GLBLoader().load(self.input_path)
        scene = SceneNormalizer().normalize(scene)

        scene, scale_metadata = ScaleNormalizer(target_length_mm=280.0).normalize(scene)
        print("Scale metadata:", scale_metadata)

        geometry_engine = GeometryAnalyzer()
        measurement_engine = FootwearMeasurementEngine()

        measurements = measurement_engine.analyze(scene)

        components = geometry_engine.extract_components(scene)
        materials = MaterialAnalyzer().analyze(scene)
        review_overrides = load_review_overrides(self.review_overrides_path)
        components, materials, review_notes = apply_review_overrides(
            components=components,
            materials=materials,
            overrides=review_overrides,
        )
        validation_issues = ValidationEngine().validate(
            measurements=measurements,
            components=components,
            materials=materials,
        )

        normalized_glb_path = export_scene_glb(
            scene,
            self.output_dir / "intermediate" / f"{self.input_path.stem}_normalized.glb",
        )

        renderer = BlenderRenderer()

        renders = renderer.render_views(
            glb_path=normalized_glb_path,
            output_dir=self.output_dir / "blender_renders",
        )

        annotated_renders = OverlayGenerator().generate_measurement_overlays(
            renders=renders,
            output_dir=self.output_dir / "annotated",
            measurements=measurements,
        )
        technical_drawings = TechnicalDrawingGenerator().generate_drawings(
            renders=renders,
            output_dir=self.output_dir / "technical_drawings",
            measurements=measurements,
        )
        annotated_renders.extend(technical_drawings)

        spec = TechPackSpec(
            model_name=self.input_path.stem,
            generated_at=datetime.now(timezone.utc).isoformat(),
            seed=self.seed,
            measurements=measurements,
            components=components,
            materials=materials,
            renders=renders,
            normalization_metadata=scale_metadata,
            annotated_renders=annotated_renders,
            validation_issues=[issue.to_dict() for issue in validation_issues],
        )

        spec.manufacturing_evidence = ManufacturingKnowledgeRetriever().retrieve_for_spec(spec)
        spec.confidence_scores = ConfidenceScorer().score(spec)
        spec.manufacturing_notes = ManufacturingNotesGenerator().generate(spec)
        spec.manufacturing_notes.extend(review_notes)
        spec.run_manifest = build_run_manifest(
            spec=spec,
            input_path=self.input_path,
            output_dir=self.output_dir,
            seed=self.seed,
        )

        save_json(spec.to_dict(), self.output_dir / "schemas" / "techpack_spec.json")
        save_json(spec.run_manifest, self.output_dir / "schemas" / "run_manifest.json")

        pdf_composer = PDFComposer()

        pdf_composer.compose_cover_sheet(
            spec,
            self.output_dir / "techpacks" / "cover_sheet.pdf",
        )

        pdf_composer.compose_measurement_sheet(
            spec,
            self.output_dir / "techpacks" / "measurement_sheet.pdf",
        )

        pdf_composer.compose_technical_drawing_sheet(
            spec,
            self.output_dir / "techpacks" / "technical_drawing_sheet.pdf",
        )

        pdf_composer.compose_bom_colorway_sheet(
            spec,
            self.output_dir / "techpacks" / "bom_colorway_sheet.pdf",
        )

        pdf_composer.compose_validation_report(
            spec,
            self.output_dir / "techpacks" / "validation_report.pdf",
        )

        print("TechPack pipeline completed.")
        print(f"Schema: {self.output_dir / 'schemas' / 'techpack_spec.json'}")
        print(f"PDF: {self.output_dir / 'techpacks' / 'cover_sheet.pdf'}")
        print(f"PDF: {self.output_dir / 'techpacks' / 'measurement_sheet.pdf'}")
        print(f"PDF: {self.output_dir / 'techpacks' / 'technical_drawing_sheet.pdf'}")
        print(f"PDF: {self.output_dir / 'techpacks' / 'bom_colorway_sheet.pdf'}")
        print(f"PDF: {self.output_dir / 'techpacks' / 'validation_report.pdf'}")

        return spec

    def _set_seed(self) -> None:
        random.seed(self.seed)
        np.random.seed(self.seed)
