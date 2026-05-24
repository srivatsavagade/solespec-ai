Take-Home Assignment
Production-Ready Footwear TechPack Generation from 3D Models
AI Engineer  •  Mid-Level  •  Time budget: 2–3 days (focused MVP)  •  Input provided

1. Context
In footwear manufacturing, a TechPack is the design-to-factory hand-off document. It tells a factory exactly what to make: every component, every material, every measurement, every colorway. Today, this is largely a manual process — designers iterate in 3D, then hand-translate the design into a TechPack via tedious spreadsheet and drawing work.
We are building the bridge: a system that ingests a textured 3D model of a shoe and emits factory-ready TechPack PDFs automatically.
This assignment asks you to build a focused MVP of that system. You will not be evaluated on completeness of every TechPack field a real factory would want — you will be evaluated on your engineering judgment, your handling of the 3D + ML side, and how cleanly the pieces compose into something a non-technical user (a designer, a sourcing manager) could actually run.
2. The Task
Build a program that:
•	Takes as input a 3D model in .glb format (binary glTF 2.0) — a single self-contained file with mesh, materials, PBR textures, and node hierarchy. We provide the file via a download link shared with this brief.
•	Produces as output a set of TechPack PDFs ready to be consumed by a factory.
"A set" is intentional. A real TechPack is often split into multiple documents (e.g., cover sheet, BOM, colorways, construction details). You decide what makes sense; we give must-haves below.
Why .glb?
It's what a modern footwear-design pipeline actually exports — a single bundled file with PBR materials (baseColor, metallicRoughness, normal, occlusion, emissive) defined to a standard spec. Working with .glb means you spend your time on the interesting problems, not on broken texture paths.
Recommended libraries for ingest: trimesh, pygltflib, Open3D (≥0.17), or Blender-as-library. Pick whatever you're comfortable with — we don't grade on library choice.
3. Required Capabilities
Your TechPack pipeline must demonstrate at least 3 of the 6 capabilities below. You choose which 3 (or more). Pick the ones where you can show depth, not just surface coverage.
#	Capability	What we expect to see
1	Multi-view rendering of the 3D model	Standard orthographic + perspective renders (top, side, front, back, 3/4) at consistent scale and lighting, suitable for a TechPack cover and reference pages.
2	3D geometry analysis (measurements, BOM from mesh)	Extract a Bill of Materials by segmenting the mesh into components (upper, sole, laces, tongue, etc.). Compute key dimensions (e.g., length, width, heel height, sole thickness) with sensible units. Show how you'd handle ambiguity.
3	Material / colorway extraction from textures	From the texture maps and material definitions, identify the dominant colors per component, propose Pantone/RAL/RGB equivalents, and infer material type where possible (leather, mesh, rubber, foam). Output a colorway sheet.
4	Auto-generated 2D technical drawings	Generate clean 2D technical drawings (top / side / exploded) with dimension callouts. Black-and-white line-art style is fine — these are working drawings, not marketing renders.
5	LLM-generated manufacturing instructions / spec text	Use an LLM to generate natural-language construction notes, stitching/assembly instructions, or QA criteria — grounded in the extracted geometry/materials, not hallucinated. Show how you constrain it.
6	Pattern / upper unfolding (2D flat patterns from 3D)	Unfold the 3D upper into 2D flat patterns (cutting templates) with seam allowances. Quantify distortion. This is the hardest capability — pick it only if you want to go deep.

Must-haves regardless of which 3 you pick:
•	Output is a set of PDFs (not a single page, not a web app).
•	PDFs have a cover page identifying the model, date, and what's inside.
•	Output is reproducible: same input + same seed → same PDF.
•	A factory person opening these PDFs should be able to understand what to make. Not perfectly — but understandably.
4. About the Provided Input
We provide one .glb file via a download link shared alongside this brief. The file contains a textured shoe model with PBR materials. Treat it as representative — your code should not be hard-coded to its specific node names, material count, or topology.
What you can rely on:
•	A valid, well-formed .glb (glTF 2.0 binary) that loads cleanly in trimesh, pygltflib, Open3D, or Blender.
•	PBR materials following the standard glTF metallic-roughness workflow (baseColorTexture, metallicRoughnessTexture, normalTexture, etc.).
•	Multiple meshes / nodes corresponding to logical components of the shoe (upper, sole, laces, etc.) — though the exact naming and segmentation is not guaranteed to be clean.
•	Reasonable scale and orientation, but verify and normalize as part of your pipeline.
What we don't promise:
•	That component meshes are perfectly named ("upper", "sole") — you may need to infer.
•	That the mesh is watertight or manifold.
•	That units are explicit (assume meters by glTF convention, but sanity-check).
Robustness note: 
If you have time, test your pipeline on a second .glb from a free source (Sketchfab, Khronos sample assets, Poly Haven). A pipeline that handles 2 shoes reasonably is a much stronger signal than one overfit to ours. This is optional, not required.
5. What's In Scope vs. Out of Scope
In scope	Out of scope (don't spend time here)
A working CLI or simple script entry point
Open-source libraries (trimesh, pygltflib, Open3D, Blender-as-library, PyMuPDF, ReportLab, etc.)
Hosted LLM APIs (OpenAI, Anthropic, etc.)
Reasonable runtime (a few minutes per model is fine)
Sensible defaults; one model is enough to demo if your code generalizes	A web UI or front-end
Authentication, user accounts, deployment
Training models from scratch
Photorealistic rendering — clarity beats beauty
Supporting formats beyond .glb (no FBX, USD, OBJ ingest required)
Handling adversarial / broken meshes
6. Deliverables
Submit a single zip (or a GitHub repo link) containing:
1.	Code — in a runnable repo. Include a README with: setup steps, how to run, expected runtime, dependencies, and where to place the input .glb.
2.	Generated TechPack PDFs — the actual output your pipeline produced on the provided input. Don't make us run it to see the result.
3.	Write-up (max 2 pages) — covering: (a) which 3 capabilities you picked and why; (b) your overall approach and why; (c) what you would do with another week; (d) where you cut corners and what you'd harden for production; (e) any assumptions you made about the input or the factory consumer.
Round 2 — live walkthrough:
Shortlisted candidates will be invited to a 45-minute live walkthrough where you'll demo the pipeline, walk through the code, and we'll dig into tradeoffs. Be ready to run it on a second .glb we may share during the call.
7. How We'll Evaluate
We're not looking for completeness. We're looking for engineering judgment. The rubric, at a high level:
What we look for	What that means in practice
Correctness & depth on chosen capabilities	Picking 3 capabilities and doing them well beats picking 6 and doing them shallowly. Show you understand the 3D / vision / ML primitives you're using, not just calling a library.
Code quality	Readable, modular, sensibly structured. Type hints where useful. Errors handled, not swallowed. Tests where they earn their keep.
Design judgment	What did you choose to include in the TechPack — and what did you cut? What's the right abstraction between "extract from 3D" and "render to PDF"? Did you over-engineer or under-engineer?
Output quality	Would a factory person actually be able to use the PDFs? Are renders clear? Are dimensions labeled? Is the layout professional?
Communication	Write-up clearly explains what you did, what you didn't, and why. README gets us running in under 10 minutes. Code comments where they help.
Handling of ambiguity	This brief is intentionally under-specified in places. We want to see what you assume, document, and decide on your own.
8. Clarifications & FAQ
This brief is intentionally not exhaustive. Real engineering work involves resolving ambiguity. Two ground rules:
•	Ask if blocked. If something prevents you from progressing, email us. We'll respond within one business day.
•	Otherwise, decide and document. If you can make a reasonable choice and move on, do that. Note the assumption in your write-up. We'd rather see your judgment than 20 clarifying questions.
Anticipated questions
Q: How polished should the PDFs look?
A: Professional but not designed. Think "engineering drawing" not "marketing asset". Clean layout, readable typography, consistent scale on renders — that's enough.
Q: Can I use commercial APIs?
A: Yes. Hosted LLMs, cloud rendering, vision APIs — all fine. Note costs in the README so we can reproduce.
Q: Do I need a GPU?
A: No. Your pipeline should run on a reasonably-spec'd laptop. If you use a GPU-only path, provide a CPU fallback or document the requirement clearly.
Q: How much LLM use is too much?
A: The LLM is a tool, not the product. We want to see you using it where it adds real value (e.g., generating manufacturing notes from structured input) — not as a shortcut around the 3D work.
Q: What if I can't get a capability working?
A: Cut it. Pick a different one, or drop to the floor of 3. A partially-working capability is worse than a clean smaller scope. Note what you tried in the write-up.
Q: What should a footwear TechPack actually contain?
A: We deliberately don't attach a sample — part of what we're evaluating is your judgment on what belongs in the output. Footwear brands and design schools publish examples publicly; a short search will give you a reasonable starting point. Don't try to match any specific format. Decide what a factory person needs to make this shoe, and produce that.
9. Final Note
This task is a real problem we work on. Have fun with it. We're more interested in how you think than in whether you tick every box.
Looking forward to seeing what you build.
