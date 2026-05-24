# SoleSpec AI Write-Up

## Selected Capabilities

I focused on four capabilities that create the strongest end-to-end TechPack signal without overfitting the assignment: multi-view rendering, 3D geometry analysis, material/colorway extraction, and auto-generated 2D technical drawings. The system also includes bounded manufacturing/spec notes as a supporting review layer, but the main capability claim is the 3D-to-TechPack document pipeline.

## System Positioning

SoleSpec AI is a factory-facing technical documentation and manufacturing review prototype that converts incomplete footwear GLB assets into industrial-style TechPack artifacts using deterministic geometry extraction, validation guardrails, Blender-based rendering, and bounded LangGraph orchestration.

The system intentionally separates correctness-critical geometric processing from probabilistic AI reasoning in order to preserve measurement reproducibility while still enabling contextual manufacturing review generation.

This is not a production footwear PLM system. It is a credible AI-assisted technical documentation prototype built around the practical constraints of real GLB assets.

## Design Principles

The system was built around five principles: deterministic geometry over probabilistic measurement inference, explicit uncertainty reporting over hidden assumptions, validation before downstream manufacturing reasoning, bounded AI orchestration instead of autonomous generation, and a structured schema as the single source of truth.

## System Flow

The system begins with GLB asset ingestion. The input model, `used_new_balance_574_classic______free.glb`, is validated and loaded as a `trimesh.Scene`, preserving geometry, material slots, and transform information for downstream processing.

The deterministic geometry pipeline is the core of the system. Manufacturing measurements must be reproducible, so geometry, scaling, measurement extraction, validation rules, and rendering are deterministic. A scene normalization stage canonicalizes the coordinate system so X = length, Y = height, and Z = width. It aligns the dominant axis, centers geometry, and moves the shoe to the ground plane. A scale normalization stage then handles unreliable GLB unit metadata by applying a canonical footwear scaling heuristic, targeting a plausible shoe length of approximately 280 mm.

The normalized scene is exported as an intermediate GLB before rendering. This matters because the measurements, overlays, and rendered views must refer to the same transformed asset. Without this boundary, a normalized measurement table could be paired with unnormalized source renders.

Manufacturing dimensions require reproducibility and numerical consistency; therefore geometry extraction and scaling were implemented deterministically rather than probabilistically.

Geometry extraction computes length, width, height, heel height, and sole thickness from transformed scene geometry. Component extraction is intentionally heuristic. Because the supplied asset is monolithic, the system uses bounding boxes, spatial heuristics, and confidence scoring rather than claiming semantic CAD segmentation.

I added a manufacturing validation engine after geometry extraction. It evaluates measurement ranges, material completeness, component segmentation confidence, and construction-sensitive values such as sole thickness. Each finding is emitted as a structured issue with severity, category, and message, then rendered into a validation report PDF.

Deterministic geometry extraction was separated from probabilistic manufacturing reasoning. Validation rules were introduced to ensure extracted measurements remained within plausible footwear manufacturing thresholds before downstream AI review.

Validation rules are heuristic manufacturing plausibility checks rather than factory-certified specification constraints. Their purpose is to make review risk visible, not to replace factory approval.

Rendering is handled by Blender because clear, consistent visual references matter more than photorealism for this task. The pipeline generates top, side, front, back, and perspective views, then creates an annotated side-view measurement overlay and side/top/front line-art style technical drawings. These assets are embedded directly into the PDFs so each page reads as a factory-facing technical document rather than a raw generated report.

The output set contains a cover sheet, measurement sheet, 2D technical drawing sheet, BOM/colorway sheet, and validation report. The BOM stays intentionally conservative: the provided asset is treated as monolithic when semantic component segmentation is not available. Rather than pretending to detect laces, upper panels, or outsole components, the document reports whole-shoe body extraction and calls out the limitation.

The pipeline was additionally validated against multiple external footwear GLB assets with differing topology complexity, geometry proportions, and metadata completeness. The validation behavior changed meaningfully per input asset: the flower sneaker triggered heel-height and thin-sole concerns, while the Miles Morales shoe primarily triggered material metadata and segmentation warnings. This demonstrated that the system is not static templating; it is an input-dependent validation and documentation pipeline.

## LangGraph Orchestration

The deterministic modules are wrapped in a lightweight LangGraph layer:

```text
ingestion -> normalization -> geometry -> validation -> rendering -> notes -> manufacturing_review -> pdf
```

This is orchestration only. The graph does not replace the core extraction logic or introduce autonomous behavior. Its purpose is to make the pipeline stages explicit and inspectable. Deterministic systems are used for geometry, scaling, measurements, validation rules, and rendering. Agentic systems are used for workflow coordination and bounded manufacturing reasoning. A validation node produces structured manufacturing findings, and a small manufacturing review node summarizes those findings into grounded QA concerns before PDF generation.

Agentic orchestration was introduced only for workflow coordination, validation interpretation, and manufacturing review tasks where probabilistic reasoning is appropriate.

The LLM-style reasoning layer is constrained. It is used for review-oriented commentary and QA interpretation, not for generating geometry or measurements.

## AI / ML Engineering Relevance

To better match an AI/ML engineering role, the system includes a bounded retrieval and confidence layer rather than relying on ungrounded generated text. A local manufacturing knowledge base is indexed with TF-IDF retrieval. The query is built from validation issues, extracted measurements, material signals, and component heuristics. Retrieved guideline IDs are persisted into the schema and summarized in the validation report.

The system also computes confidence scores for geometry extraction, material extraction, component segmentation, and factory readiness. These scores are not presented as learned truth; they are audit signals derived from extraction completeness, validation severity, scale normalization, and segmentation uncertainty. This mirrors a practical ML engineering pattern: combine deterministic preprocessing, retrieval evidence, confidence scoring, and inspectable outputs.

Finally, each run writes a manifest with input path, seed, environment details, selected capabilities, normalization metadata, confidence scores, output files, and validation counts. This makes the pipeline easier to debug, reproduce, and discuss as an AI service rather than a one-off script.

## Confidence and Domain Scope

The provided GLB assets lacked reliable semantic segmentation metadata. Confidence scoring and validation reporting were therefore introduced to surface extraction uncertainty explicitly.

The infrastructure pipeline is mostly domain-agnostic: load asset, normalize, analyze, validate, render, and assemble documents. The semantic extraction and validation logic are currently specialized for footwear.

The strongest architectural boundary is the deterministic versus agentic split. Geometry, scaling, measurements, validation rules, and rendering are deterministic because they affect correctness-critical outputs. LangGraph is used for orchestration, validation interpretation, and bounded manufacturing review where contextual reasoning is useful.

## Structured Schema

`outputs/schemas/techpack_spec.json` acts as the canonical manufacturing representation. The PDFs, overlays, validation report, and manufacturing notes are derived from this structured schema, which keeps the document generation path reproducible and inspectable. The schema includes normalization metadata, measurement values, component heuristics, material RGB/hex palette fields, color source, retrieval evidence, confidence scores, validation findings, and render references.

`outputs/schemas/run_manifest.json` provides a lightweight audit trail for reproducibility and service-readiness.

## Assumptions

- The input is a valid `.glb` model that can be loaded by `trimesh` and Blender.
- If units are implausible, the model is rescaled to a target footwear length of 280 mm.
- X is normalized as length, Y as height, and Z as width.
- Monolithic assets should be reported honestly instead of force-segmented.
- RGB/hex color values are extracted from GLB materials or texture-derived dominant colors; Pantone/RAL mapping is intentionally left as a factory confirmation step.
- Extracted dimensions are useful for review but should be verified against a physical production sample.
- Generated technical drawings are line-art references derived from rendered views, not CAD-grade pattern files or certified factory drawings.

## Tradeoffs

I prioritized credible output quality and clear engineering boundaries over deeper research features. Pattern unfolding and robust component segmentation are intentionally out of scope because they would require stronger assumptions about topology, mesh quality, and semantic labels. The current implementation shows the full document-generation path while clearly marking low-confidence areas.

The provided GLB asset lacked semantic footwear segmentation and reliable manufacturing metadata. The system therefore used deterministic geometric heuristics, validation rules, and confidence reporting rather than claiming full production-grade CAD intelligence.

The remaining weaknesses are intentional MVP boundaries rather than hidden capabilities. Component extraction is heuristic, not semantic footwear decomposition. Material intelligence is metadata-based and does not yet classify textures or reason over supplier materials. Validation rules are plausibility heuristics, not factory-certified tolerances. The `280 mm` scale normalization prior is useful for missing GLB units, but it remains an assumption that must be surfaced.

The lightweight agentic layer is a design choice. The graph provides structured orchestration and bounded review generation without letting probabilistic reasoning generate measurements or production-critical geometry.

## Engineering Review

The pipeline became stronger because it evolved around real constraints: coordinate ambiguity, scale ambiguity, missing metadata, monolithic geometry, rendering issues, and uncertainty handling. Solving those constraints produced a more believable architecture than a flashy demo built around ideal inputs.

## What I Would Harden Next

With another week, I would broaden regression coverage across more shoe GLBs, persist scale/orientation metadata directly into the schema, improve embedded texture and color extraction, and add more robust runtime checks around Blender availability. If component segmentation were required, I would first evaluate whether the source node hierarchy or material assignments provide reliable segmentation signals before applying geometric clustering.
