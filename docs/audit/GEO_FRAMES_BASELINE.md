Status: BASELINE
Last Updated: 2026-03-09
Version: 1.0.0
Scope: GEO-2 deterministic reference frames, floating-origin policy, and precision baseline.

# GEO Frames Baseline

## 1) Scope

GEO-2 freezes the deterministic reference-frame layer on top of GEO-0 topology/metric/projection contracts and GEO-1 spatial identity.

The authoritative doctrine is:

- `docs/geo/REFERENCE_FRAMES_AND_PRECISION.md`

Relevant invariants and contracts upheld:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A3 Observer/renderer/truth separation
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` C1 Version semantics
- `docs/canon/constitution_v1.md` C3 CompatX obligations
- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`
- `docs/geo/REFERENCE_FRAMES_AND_PRECISION.md`

## 2) Retro Audit Summary

Retro-consistency findings are recorded in `docs/audit/GEO2_RETRO_AUDIT.md`.

The audit confirmed:

- truth and camera surfaces already distinguish `frame_id` from local coordinates, but only as labels
- ROI and observation still use origin-distance heuristics instead of frame-aware position distances
- field sampling already has a clean migration seam through GEO partition APIs
- renderer projection already routes through GEO, but render rebasing was not yet a named deterministic policy

GEO-2 therefore stayed additive:

- no domain-wide coordinate rewrite
- no truth tick-order change
- no render-to-truth mutation path

## 3) Schema Baseline

Strict v1.0.0 schema set added:

- `schema/geo/frame_node.schema`
- `schema/geo/frame_transform.schema`
- `schema/geo/position_ref.schema`

CompatX integration added corresponding entries in:

- `tools/xstack/compatx/version_registry.json`

## 4) Frame Graph Model

GEO-2 now freezes the canonical frame surfaces:

- `frame_node`
- `frame_transform`
- `position_ref`

Runtime APIs now live in:

- `src/geo/frame/frame_engine.py`
- `src/geo/frame/domain_adapters.py`

Key rules now enforced by implementation:

- frame nodes are anchored by topology, metric, chart, and `geo_cell_key`
- frame traversal resolves through stable parent chains and deterministic LCA selection
- frame graph hash is deterministic and cacheable
- truth positions are represented as local coordinates relative to an explicit frame
- cross-frame distance queries route through frame conversion plus GEO metric evaluation

## 5) Render Floating-Origin Rules

Render-only rebasing now lives in:

- `src/geo/render/floating_origin_policy.py`

Frozen GEO-2 render rules:

- choose rebase offset deterministically from camera position in a target frame
- quantize offset by declared rebase quantum
- convert authoritative positions through the GEO frame graph first
- derive rebased render-local coordinates only after frame conversion
- assert that truth refs remain unchanged after render conversion

This preserves the observer/render/truth separation:

- truth remains frame-local and hash-stable
- render may rebase freely as a derived presentation surface
- rebasing does not alter proof or replay hashes

## 6) Domain Adapter Baseline

GEO-2 added thin adapter surfaces rather than broad domain migrations:

- `field_sampling_position(...)`
- `field_sampling_cell_key(...)`
- `roi_distance_mm(...)`

These helpers establish the required route for future migrations:

- `position_ref -> frame conversion -> field sampling`
- `position_ref -> frame conversion -> ROI distance`

Existing FIELD/ROI runtime logic remains behaviorally unchanged in this phase.

## 7) Proof And Replay Baseline

Proof/replay integration added:

- `tools/geo/tool_replay_frame_window.py`
- control proof bundle GEO extensions now accept:
  - `frame_graph_hash_chain`
  - `position_ref_hash_chain`

This keeps schema compatibility intact because control proof bundle extensions remain open-map.

## 8) Enforcement Baseline

RepoX scaffolding added:

- `INV-NO-RAW-GLOBAL-COORDS`
- `INV-RENDER-REBASING-NO-TRUTH-MUTATION`

AuditX analyzers added:

- `E336_RAW_GLOBAL_COORD_SMELL`
- `E337_RENDER_WRITES_TRUTH_SMELL`

As with GEO-1, these rules are intentionally narrow:

- they protect the canonical GEO-2 frame and render policy surfaces
- they do not pretend legacy camera/ROI heuristics are already fully migrated
- they provide a ratchet for future GEO migrations

## 9) Contract And Schema Impact

Changed:

- new GEO doctrine for frame graphs, truth-local positions, and fixed-point precision policy
- new schema family for frame nodes, frame transforms, and position refs
- new deterministic frame graph runtime and render-only floating-origin runtime
- new frame-based domain adapter APIs for sampling and ROI distance
- control proof bundle extensions may now carry frame graph and position-ref hash chains
- new RepoX/AuditX/TestX scaffolding for frame discipline

Unchanged:

- process-only mutation invariant
- observer/renderer/truth separation
- TruthModel tick ordering
- existing camera/session authored fields
- worldgen/orbital integration responsibilities
- existing GEO-1 object identity semantics

## 10) Validation Snapshot

Executed during GEO-2 baseline:

- RepoX STRICT:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - result: `pass`
  - findings: `17` warnings, `0` refusals after topology map regeneration
- AuditX STRICT:
  - `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - result: `pass`
  - findings: `2253`
  - promoted blockers: `0`
- targeted GEO-2 TestX suite:
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_frame_transform_deterministic,test_position_conversion_roundtrip,test_floating_origin_no_truth_mutation,test_large_scale_precision_stability,test_cross_platform_frame_hash_match`
  - result: `pass`
- GEO frame replay verifier:
  - `py -3 tools/geo/tool_replay_frame_window.py`
  - result: `complete`
  - frame graph hash chain: `782572113a259c4f3a79bdeb414ef1e1ff18e5b91ebbba43efbb408505da650d`
  - position ref hash chain: `63222f74b3a87ae336a5f39206c091094e0cca7f2d44eaff385c285b29691401`
  - deterministic fingerprint: `6d0ed3c87038c8caa78e547fe466748072860665820db284f9abdd73ed105e2b`
- topology map regeneration:
  - `py -3 tools/governance/tool_topology_generate.py --repo-root .`
  - result: `complete`
  - deterministic fingerprint: `aa2f2991cec478fb6efa36f87011c51eda9a252dca0aa697a2b4f344fcc7a7d4`
- strict build:
  - `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.geo2 --cache on --format json`
  - result: `complete`
  - canonical content hash: `9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`

## 11) Readiness For GEO-3

GEO-2 is ready for GEO-3 metric query work because:

- truth positions are now expressible as frame-local refs
- frame graph conversion is deterministic and cacheable
- render-only rebasing has an explicit policy boundary
- proof surfaces can now carry frame and position hash chains
- field/ROI migrations have stable adapter entry points

Deferred beyond GEO-2:

- orbital propagation and authored celestial motion
- broad migration of legacy camera/ROI heuristics
- richer rotation semantics beyond the current deterministic baseline subset
- bounded geodesic query expansion and metric engine generalization in GEO-3
