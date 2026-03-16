Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: GEO-3 deterministic metric queries, geodesic stubs, neighborhood enumeration, and cache baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO Metric Baseline

## 1) Scope

GEO-3 freezes the deterministic metric-query layer on top of GEO-0 topology and metric constitutions, GEO-1 cell identity, and GEO-2 reference frames.

The authoritative doctrine is:

- `docs/geo/METRIC_QUERY_ENGINE.md`

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
- `docs/geo/METRIC_QUERY_ENGINE.md`

## 2) Retro Audit Summary

Retro-consistency findings are recorded in `docs/audit/GEO3_RETRO_AUDIT.md`.

The audit confirmed:

- direct Euclidean distance helpers still existed in mobility and constrained-motion runtime paths
- FIELD and ROI already had adapter seams that could absorb GEO metric routing without broad rewrites
- POLL neighborhood traversal already depended on cell adjacency but still needed canonical GEO neighbor ordering
- no canon-safe path existed for alternate metrics unless distance and neighborhood queries became explicit GEO surfaces

GEO-3 therefore stayed targeted:

- no PDE or worldgen work
- no change to Truth tick ordering
- no render-to-truth mutation path
- no silent float leakage outside declared TOL quantization

## 3) Registry and Profile Baseline

New baseline registries added:

- `data/registries/metric_policy_registry.json`
- `data/registries/geodesic_approx_policy_registry.json`

Metric profiles now declare the policy surfaces needed by GEO-3 through registry extensions:

- `metric_policy_id`
- `geodesic_approx_policy_id`

Partition profiles now declare bounded neighborhood policy through registry extensions:

- `max_neighbors`

Representative policies frozen by GEO-3:

- `metric.euclidean_exact`
- `metric.torus_wrap_exact`
- `metric.spherical_geodesic_stub`
- `metric.hyperbolic_stub`
- `metric.custom_plugin_stub`
- `geodesic.none`
- `geodesic.spherical_linear_approx`
- `geodesic.iterative_stub`

## 4) Metric Policy Baseline

Runtime implementation now lives in:

- `src/geo/metric/metric_engine.py`
- `src/geo/metric/metric_cache.py`

Frozen GEO-3 query surfaces:

- `geo_distance(...)`
- `geo_geodesic(...)`
- `metric_query_proof_surface(...)`

Key rules now enforced by implementation:

- frame-aware positions resolve through GEO-2 frame conversion before metric evaluation
- metric selection is driven by `metric_profile_id` and registry policy metadata
- Euclidean distance uses deterministic fixed-point quantization and integer-root style rounding discipline
- torus distance computes minimal wrapped deltas using topology-declared periodic extents
- spherical geodesic uses a deterministic bounded approximation and returns an explicit error bound
- every distance and geodesic result carries `{distance_value, error_bound}`

## 5) Error Bounds And TOL Discipline

GEO-3 freezes explicit bounded-error behavior rather than implicit floating-point trust.

Baseline error policy:

- Euclidean exact:
  - error bound `0` after fixed-point quantization
- Torus wrap exact:
  - error bound `0` after wrapped-delta selection and fixed-point quantization
- Spherical geodesic stub:
  - deterministic linearized arc approximation
  - declared bounded error derived from profile policy and rounded through TOL
- Geodesic fallbacks:
  - when no distinct geodesic policy applies, GEO returns the distance result with its declared bound

This keeps all numeric surfaces inside TOL discipline:

- quantized inputs
- deterministic rounding
- explicit error reporting
- cacheable proof surface hashing

## 6) Neighborhood Enumeration Rules

Deterministic neighborhood runtime now lives in:

- `src/geo/metric/neighborhood_engine.py`

Frozen GEO-3 neighborhood rules:

- `geo_neighbors(...)` is the canonical neighborhood surface
- legacy GEO-0 positional call ordering remains supported for compatibility
- GEO-3 explicit parameter ordering is also supported for forward migration
- grid partitions enumerate bounded integer offsets, filter by metric radius, and sort deterministically
- torus partitions canonicalize wrapped indices into the topology fundamental domain before ordering
- sphere-atlas partitions use deterministic atlas adjacency and preserve compact alias compatibility surfaces
- profile-driven `max_neighbors` limits are enforced before returning results

The result is topology-portable and replay-stable cell adjacency:

- deterministic ordered lists
- no ad hoc domain-local coordinate walking
- no hidden dependence on ambient Euclidean assumptions

## 7) Domain Integration Summary

GEO-3 added thin but authoritative migration hooks in domain runtime surfaces:

- MOB:
  - `src/mobility/geometry/geometry_engine.py`
  - `src/mobility/micro/constrained_motion_solver.py`
  - direct Euclidean segment and path length calculations now route through `geo_distance(...)`
- FIELD:
  - `src/fields/field_engine.py`
  - new GEO adapters expose `geo_field_sample_position(...)`, `geo_field_sample_cell_key(...)`, and `geo_field_distance_mm(...)`
- POLL:
  - `src/pollution/dispersion_engine.py`
  - cell-neighbor traversal now routes through `geo_neighbors(...)`
- ROI:
  - `src/system/roi/system_roi_scheduler.py`
  - new `system_roi_distance_query(...)` routes radius checks through GEO metric APIs

These are deliberate adapter migrations, not broad domain rewrites. GEO-3 freezes the rule that future domain distance and neighborhood logic must enter through GEO surfaces.

## 8) Proof, Replay, And Cache Baseline

Proof/replay integration added:

- `tools/geo/tool_verify_metric_stability.py`
- control proof bundle GEO extensions now accept:
  - `topology_profile_ids`
  - `metric_profile_ids`
  - `metric_query_hash_chain`

Deterministic cache behavior added in:

- `src/geo/metric/metric_cache.py`

Frozen cache rules:

- cache key is derived from query inputs, profile identifiers, and version surface
- results are pure and reusable across runs
- eviction order is deterministic by stable key ordering
- cache is bypassed in FULL reference mode to preserve purity verification

## 9) Enforcement Baseline

RepoX scaffolding added:

- `INV-NO-RAW-DISTANCE-CALCULATION`
- `INV-METRIC-PROFILE-DECLARED`

AuditX analyzers added:

- `E338_RAW_SQRT_USAGE_SMELL`
- `E339_HARDCODED_DISTANCE_SMELL`

The GEO enforcement surface now also has complete analyzer registration for the earlier GEO-1 and GEO-2 smell families, so GEO metric discipline lands on top of a consistent GEO audit chain rather than a partial registry.

## 10) Contract And Schema Impact

Changed:

- new GEO doctrine for distance, geodesic approximation, bounded error, and cache semantics
- new metric and geodesic policy registries
- metric and partition registry extensions for declared policy binding and neighbor caps
- new deterministic metric, neighborhood, and cache runtime APIs
- domain adapter surfaces for FIELD, POLL, MOB, and ROI metric routing
- control proof bundle extensions may now carry metric and topology query hash context
- new RepoX/AuditX/TestX scaffolding for metric discipline

Unchanged:

- process-only mutation invariant
- observer/renderer/truth separation
- TruthModel tick ordering
- worldgen content responsibilities
- heavy PDE solver responsibilities
- existing GEO-1 identity semantics
- render-only floating-origin policy boundaries

## 11) Validation Snapshot

Executed during GEO-3 baseline:

- RepoX STRICT:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - result: `pass`
  - findings: `17`
- AuditX STRICT:
  - `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - result: `pass`
  - findings: `2251`
  - promoted blockers: `0`
- targeted GEO-3 TestX suite:
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_euclidean_distance_deterministic,test_torus_wrap_distance_correct,test_spherical_stub_geodesic_bounded_error,test_neighbors_deterministic_order,test_cross_platform_metric_hash_match`
  - result: `pass`
- compatibility GEO neighbor regression subset:
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_euclidean_distance_deterministic,test_torus_wrap_distance_correct,test_spherical_stub_geodesic_bounded_error,test_neighbors_deterministic_order,test_cross_platform_metric_hash_match,test_neighbors_deterministic_r2_r3`
  - result: `pass`
- GEO metric stability verifier:
  - `py -3 tools/geo/tool_verify_metric_stability.py`
  - result: `complete`
  - tool deterministic fingerprint: `110be6cdf0eac104510ec7bd1b8c4bce777db487395bb72b02e80c69e61e0776`
  - proof surface deterministic fingerprint: `57188ad69d5704d8c761dfa5bfa4ada35331820d2ebfcafe70af994ca88dcdfa`
  - metric query hash chain: `c9401c6cc72b85b7c5b2d920010c83a3dac28fc389108580cee79715e9f60ee0`
  - run hash: `de237390a0b94f1a31f9bacbcf288adf4225720b18e83529fc2a456a8d71a579`
- topology map regeneration:
  - `py -3 tools/governance/tool_topology_generate.py --repo-root .`
  - result: `complete`
  - deterministic fingerprint: `6633e1dbc5b515c26b81e342152324b88214ef5f9d8423307b231c71aed7cdca`
- strict build:
  - `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.geo3 --cache on --format json`
  - result: `complete`
  - canonical content hash: `9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`

## 12) Readiness For GEO-4

GEO-3 is ready for GEO-4 field sampling and partition binding because:

- distance and geodesic queries now have deterministic profile-driven routing
- neighborhood traversal is topology-aware and bounded
- field, pollution, mobility, and ROI seams now have canonical GEO metric entry points
- proof surfaces can carry topology, metric, and query-hash context
- deterministic caching is available without changing authoritative semantics

Deferred beyond GEO-3:

- richer bounded geodesic algorithms beyond the current spherical stub
- hyperbolic and custom plugin implementations beyond registry placeholders
- broad elimination of all legacy domain heuristics outside the migrated adapter surfaces
- GEO-4 field sampling and partition-binding semantics
