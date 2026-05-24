# SoleSpec Manufacturing Review Knowledge Base

## [GEO-001] Normalize and Verify Footwear Dimensions
When source 3D assets do not provide reliable units, normalize dimensions before generating factory documents. Any normalized measurements should be treated as review measurements and verified against source CAD, a last, or a physical sample before production approval.

## [GEO-002] Heel and Sole Plausibility Checks
Athletic footwear with high heel height or very thin sole estimates should be reviewed by product engineering. Heel height, outsole thickness, midsole stack, and ground contact profile affect comfort, stability, tooling, and production feasibility.

## [MAT-001] Colorway Approval
RGB or texture-derived colors are useful for review but are not final factory color standards. Factory handoff should confirm approved Pantone, RAL, material swatch, or brand color code before production.

## [MAT-002] Material Metadata Completeness
If a GLB lacks explicit material type, supplier code, or texture source metadata, mark material confidence as limited. Do not infer leather, mesh, foam, or rubber beyond what material names, textures, or source documentation support.

## [SEG-001] Component Segmentation Confidence
Monolithic meshes should not be force-labeled as upper, laces, tongue, midsole, or outsole. Report segmentation uncertainty and request cleaner component hierarchy, material groups, or CAD source files for production-grade BOM extraction.

## [QA-001] Factory Readiness Review
A TechPack generated from 3D extraction should include explicit assumptions, validation warnings, and confidence scores. Medium or high validation findings should trigger manual review before factory release.
