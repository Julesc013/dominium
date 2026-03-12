Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO10 Retro Audit

Status: complete  
Scope: GEO envelope hardening audit across geometry usage, render/view separation, and remaining portability drift points.

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A3` Observer/renderer/truth separation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `INV-GEO-API-ONLY-FOR-DOMAIN-DISTANCE`
- `INV-NO-TRUTH-IN-UI`
- `INV-VIEWS-MUST-USE-LENS`
- `INV-OVERLAY-MERGE-DETERMINISTIC`

## Audit Summary

The repository is largely on the intended GEO contract:

- direct domain distance math has already been routed through GEO surfaces in the remaining checked runtime code
- neighborhood iteration in pollution is GEO-based
- projection and lens runtime remains separated from authoritative truth mutation
- overlay merge, geometry edits, and worldgen already expose replay/proof surfaces

Remaining drift points are mostly local-micro or render-space assumptions rather than canonical truth-layer violations.

## Findings

### 1. Mobility local-micro helpers still hardcode `r3 + euclidean`

Observed:

- `src/mobility/geometry/geometry_engine.py`
- `src/mobility/micro/constrained_motion_solver.py`

Both route distance through `geo_distance`, which is good, but they hardcode:

- `geo.topology.r3_infinite`
- `geo.metric.euclidean`

Impact:

- acceptable for current declared local micro physics
- not yet portable to non-Euclidean or non-`R^3` micro traversal without an adapter/profile handoff

Migration note:

- future mobility-local geometry helpers should accept frame/topology/metric context from GEO profile bindings instead of embedding `r3_infinite + euclidean`

### 2. Renderers still perform cartesian camera-space subtraction on RenderModel payloads

Observed:

- `src/client/render/renderers/software_renderer.py`
- `src/client/render/render_model_adapter.py`

The software renderer subtracts `position_mm` from `camera.position_mm` and applies local camera rotations directly.

Impact:

- this is acceptable because it operates on RenderModel, not TruthModel
- it is still a geometry portability limit for non-cartesian render backends, atlas views, and higher-dimensional slice visualizations

Migration note:

- future hardware/software renderers should increasingly consume GEO projection outputs or explicit render-space transforms instead of assuming 3D cartesian camera-space math

### 3. UI preview/inspection flows read truth anchors, not raw truth payloads

Observed:

- `src/client/interaction/preview_generator.py`
- `src/client/interaction/inspection_overlays.py`
- `src/client/interaction/interaction_dispatch.py`

These flows read `perceived_model.truth_overlay.state_hash_anchor` as an epistemic gate for expensive derived previews/inspection overlays.

Impact:

- current behavior is not a direct truth leak because the read is to a hash anchor/gating surface
- it is still a drift point worth tracking because additional preview features could expand beyond anchor reads if not kept constrained

Migration note:

- preserve anchor-only access
- if richer GEO views are needed, route them through GEO lens/projection artifacts rather than expanding direct preview access to truth-derived structures

### 4. GEO portability enforcement already catches most remaining raw geometry smells

Observed:

- RepoX GEO invariant passes exist through GEO-9
- AuditX analyzers already cover raw XYZ, hardcoded dimension, projection truth leak, raw sqrt, hardcoded distance, direct terrain writes, and nondeterministic merge smells

Impact:

- GEO-10 can focus on integrated stress/proof/regression coverage instead of broad runtime refactors

## Domain Status Check

### Metric and neighborhood usage

Compliant surfaces observed:

- `src/pollution/dispersion_engine.py` uses `geo_neighbors`
- `src/client/render/representation_resolver.py` uses `geo_distance`
- `src/fields/field_engine.py` uses GEO distance and GEO cell mapping
- `src/geo/frame/domain_adapters.py` routes field sampling and ROI distance through GEO

### Raw coordinate assumptions still present

Contained assumptions observed:

- render-space camera subtraction in software renderer
- local micro mobility helpers using `r3_infinite + euclidean`
- interaction overlays and panels still operate on render-space `position_mm`

These are derived/local assumptions, not authoritative truth mutations.

### UI truth leak check

No direct UI reads of authoritative TruthModel payloads were identified in this audit pass.

Observed accesses were:

- truth hash anchor gating
- perceived model overlays
- render-model positions

That remains within the intended observer/render separation, but GEO-10 should keep this under regression lock.

## Fix List

1. Add a GEO-wide stress scenario generator covering multi-topology, views, overlays, edits, and replay.
2. Add a GEO stress harness that asserts no truth leaks, bounded iterations, stable IDs, and stable replay hashes.
3. Add explicit GEO degradation ordering for derived views and bounded path budgets.
4. Add replay tools that verify the combined GEO window rather than only individual GEO subsystems.
5. Add bounded META-REF evaluators for small GEO metric, neighborhood, and overlay fixtures.
6. Add a GEO regression baseline with explicit `GEO-REGRESSION-UPDATE` tag gating.
7. Extend RepoX/AuditX so GEO envelope regressions fail before domain drift accumulates.
8. In a later mobility-focused series, remove embedded `r3_infinite + euclidean` assumptions from local micro helpers by threading profile/frame context through the call sites.
