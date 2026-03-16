Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Renderer Baseline Report (RND-2)

Date: 2026-02-26  
Status: Baseline complete (null + software renderers, derived snapshot pipeline)

## 1) Implemented Renderer Capabilities

### Null Renderer (`renderer_id=null`)

1. Consumes `RenderModel` only.
2. Produces deterministic derived artifacts:
   - `frame_summary.json`
   - `frame_layers.json`
   - `render_snapshot.json`
3. Produces no pixels.
4. Deterministic summary hash/fingerprint from canonical serialization.

### Software Renderer (`renderer_id=software`)

1. CPU rendering baseline with no asset dependencies.
2. Supported primitive baseline:
   - box
   - sphere
   - cylinder
   - capsule (approx)
   - plane
   - line
   - glyph fallback marker
3. Perspective camera projection + depth buffer.
4. Flat shading from procedural material base color.
5. Optional wireframe overlay.
6. Image output via `.ppm` artifact plus summary/snapshot metadata.

## 2) Snapshot Schema Summary

Added strict schemas:

1. `schema/render/render_snapshot.schema`
2. `schema/render/frame_summary.schema`

Snapshot payload includes:

1. RenderModel identity linkage (`render_model_hash`, tick/viewpoint/profile)
2. Renderer identity and output format
3. deterministic `summary_hash`
4. optional informational `pixel_hash`
5. output refs (`image_ref`, `summary_ref`, `layers_ref`)

## 3) Determinism Guarantees

Guaranteed deterministic:

1. Null renderer summary fields and summary hash
2. Snapshot metadata structure and IDs for identical inputs
3. Cache key behavior for identical `(render_model_hash, renderer_id, resolution, wireframe)`
4. Derived artifact path structure (`run_meta/render_snapshots/<snapshot_id>/...`)

Pixel determinism disclaimer:

1. Software renderer pixel hashes are informational.
2. Cross-platform pixel-perfect equality is not required.
3. Canonical simulation determinism relies on RenderModel/summaries, not pixel bytes.

## 4) Derived Storage and Cache

Implemented in capture pipeline:

1. Deterministic storage root default:
   - `run_meta/render_snapshots/<snapshot_id>/`
2. Derived cache store:
   - `.xstack_cache/render_snapshots/snapshot_cache_index.json`
3. Cache key:
   - `(render_model_hash, renderer_id, width, height, wireframe)`
4. Cache hits reuse existing derived artifacts; no simulation mutation.

## 5) Guardrails

### RepoX invariants

1. `INV-RENDERER-CONSUMES-RENDERMODEL-ONLY`
2. `INV-RENDER_SNAPSHOTS_DERIVED_ONLY`

### AuditX analyzers

1. `E50_RENDERER_TRUTH_LEAK_SMELL` (`RendererTruthLeakSmell`)
2. `E51_RENDER_SNAPSHOT_MISCLASSIFIED_SMELL` (`RenderSnapshotMisclassifiedSmell`)

### TestX coverage

1. `testx.render.null_renderer_summary_deterministic`
2. `testx.render.render_snapshot_schema_valid`
3. `testx.render.software_renderer_produces_image`
4. `testx.render.renderer_truth_isolation`
5. existing RND-1 render tests retained

## 6) Extension Points

1. RND-3 hardware backend can consume unchanged `RenderModel`/snapshot contracts.
2. RND-4 interaction layer can reuse snapshot artifacts for inspect/debug workflows.
3. Material/visual enrichment can remain registry-driven without changing truth simulation semantics.

## 7) Gate Execution (RND-2 Final)

1. RepoX PASS
   - `py -3 -m tools.xstack.repox.check --profile STRICT`
2. AuditX run PASS
   - `py -3 -m tools.xstack.auditx.check --profile STRICT`
3. TestX PASS (RND-2 suite + render contract regression subset)
   - `py -3 tools/xstack/testx/runner.py --profile STRICT --subset testx.render.null_renderer_summary_deterministic,testx.render.render_snapshot_schema_valid,testx.render.software_renderer_produces_image,testx.render.renderer_truth_isolation,testx.render.no_truth_access,testx.render.render_model_deterministic_ordering,testx.render.representation_rule_resolution_deterministic,testx.render.no_assets_required`
4. strict build PASS
   - `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.rnd2 --cache on --format json`
5. ui_bind check PASS
   - `py -3 tools/xstack/ui_bind.py --repo-root . --check`
