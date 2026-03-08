Status: BASELINE
Last Updated: 2026-03-08
Version: 1.0.0
Scope: GEO-0 Geometry and Topology constitutional baseline.

# GEO Constitution Baseline

## 1) Constitutional Scope

GEO-0 freezes the geometry portability contract around four first-class profiles:

- `SpaceTopologyProfile`
- `MetricProfile`
- `GeometryPartitionProfile`
- `ProjectionProfile`

Universe space is now defined as topology + metric + partition + projection, rather than by ad hoc axis arithmetic. The constitutional source is `docs/geo/GEO_CONSTITUTION.md`.

## 2) Retro Audit Summary

Retro-consistency findings are recorded in `docs/audit/GEO0_RETRO_AUDIT.md`.

Migration points identified:

- MOB movement and ROI logic still contains local Cartesian assumptions that must eventually route through GEO neighbor and distance APIs.
- FIELD sampling previously relied on direct grid cell formatting and now has a GEO partition routing path; remaining chart-local assumptions are documented for later cleanup.
- POLL dispersion had direct neighbor-map dependence; GEO neighbor enumeration is now the preferred deterministic path with compatibility fallback.
- SYS ROI scheduling and renderer distance/projection behavior exposed direct XYZ arithmetic patterns that are now tracked under GEO portability enforcement.
- Rendering/camera projection paths require epistemic gating through Lens requests rather than truth-side projection shortcuts.

No schema migration was performed in GEO-0; the audit captures target migration points only.

## 3) Schema and Registry Baseline

Strict v1.0.0 schema set added:

- `schema/geo/space_topology_profile.schema`
- `schema/geo/metric_profile.schema`
- `schema/geo/partition_profile.schema`
- `schema/geo/projection_profile.schema`
- `schema/geo/geo_query.schema`

CompatX integration added corresponding schema entries in `tools/xstack/compatx/version_registry.json`.

Baseline registries added:

- `data/registries/space_topology_profile_registry.json`
- `data/registries/metric_profile_registry.json`
- `data/registries/partition_profile_registry.json`
- `data/registries/projection_profile_registry.json`

Representative baseline profiles now include:

- topologies: `geo.topology.r1_infinite`, `geo.topology.r2_infinite`, `geo.topology.r3_infinite`, `geo.topology.torus_r2`, `geo.topology.torus_r3`, `geo.topology.sphere_surface_s2`, `geo.topology.cube_identified_stub`, `geo.topology.r4_stub`
- metrics: `geo.metric.euclidean`, `geo.metric.torus_wrap`, `geo.metric.spherical_geodesic_stub`, `geo.metric.hyperbolic_stub`
- partitions: `geo.partition.grid_zd`, `geo.partition.octree_stub`, `geo.partition.sphere_tiles_stub`, `geo.partition.atlas_tiles`
- projections: `geo.projection.ortho_2d`, `geo.projection.perspective_3d`, `geo.projection.atlas_unwrap_stub`, `geo.projection.slice_nd_stub`

## 4) Kernel API Baseline

Pure deterministic kernel APIs are implemented in `src/geo/kernel/geo_kernel.py`:

- `geo_neighbors(cell_key, topology_profile_id, radius, metric_profile_id)`
- `geo_distance(pos_a, pos_b, topology_profile_id, metric_profile_id)`
- `geo_transform(pos, from_chart, to_chart)`
- `geo_project(pos, topology_profile_id, projection_profile_id)`
- `geo_partition_cell_key(position_mm, topology_profile_id, partition_profile_id)`

Kernel guarantees frozen at GEO-0:

- deterministic ordering for neighbor enumeration
- pure results as a function of inputs and profile parameters
- deterministic cache keys through hashed query payloads
- bounded algorithm surfaces with declared stub/error behavior
- no world generation, pathfinding, or geometry editing responsibility

## 5) Profile Override Integration

GEO profiles are now first-class unified profile bindings through `src/geo/profile_binding.py`.

Universe identity may declare default GEO bindings:

- `topology_profile_id`
- `metric_profile_id`
- `partition_profile_id`
- `projection_profile_id`

Session/profile overrides are explicit and logged. Dimension-breaking topology overrides are refused with:

- `refusal.geo.profile_missing`
- `refusal.geo.dimension_change`

This preserves the no-mode-flag rule and keeps geometry selection under profile composition rather than runtime branching.

## 6) Enforcement Baseline

RepoX scaffolding added:

- `INV-GEO-API-ONLY-FOR-DOMAIN-DISTANCE`
- `INV-NO-HARDCODED-DIMENSION-ASSUMPTIONS`
- `INV-PROJECTION-EPITEMIC-GATED`

AuditX analyzers added:

- `E331_RAW_XYZ_DISTANCE_SMELL`
- `E332_HARDCODED_DIMENSION_SMELL`
- `E333_PROJECTION_TRUTH_LEAK_SMELL`

Initial runtime integrations completed for GEO-0 enforcement posture:

- FIELD partition cell routing now uses GEO partition helpers
- POLL dispersion neighbor enumeration can use GEO topology neighbors
- renderer LOD distance uses GEO metric distance
- software projection path routes through GEO projection

## 7) Invariants and Contract Impact

Relevant invariants and constitutional rules upheld:

- process-only mutation invariant remains unchanged
- observer/renderer/truth separation remains unchanged
- no mode flags; profile composition only
- deterministic ordering, replayability, and cacheability preserved
- cross-shard adjacency and metric queries remain boundary-artifact mediated by constitution

Contract/schema impact:

- changed: new GEO constitutional document, GEO schema family, GEO registries, universe/profile bindings, refusal contract entries, RepoX/AuditX/TestX scaffolding
- unchanged: canonical mutation model, law authority model, replay semantics, sharding doctrine, worldgen/pathfinding/editing responsibilities

## 8) Validation Snapshot

Executed during GEO-0 baseline:

- targeted schema/example validation for updated `universe_identity`
- targeted kernel determinism checks for R2, R3, torus-wrap, sphere-atlas, and projection stub behavior
- topology map regeneration:
  - `py -3 tools/governance/tool_topology_generate.py --repo-root .`
  - result: `complete`
  - deterministic fingerprint: `514019fc7b7828d7c76cba357b3eb88a98a428f3870a7e18d5750fbf3df3fcac`
- AuditX STRICT:
  - `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - result: `pass`
  - promoted blockers: `0`
- targeted TestX GEO suite:
  - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_geo_profiles_registry_valid,test_neighbors_deterministic_r2_r3,test_torus_wrap_distance_deterministic,test_sphere_surface_stub_neighbors_deterministic,test_projection_stub_deterministic,test_profile_override_logged`
  - result: `pass`
- strict build:
  - `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.geo0 --cache on --format json`
  - result: `complete`
  - canonical content hash: `9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`

Global repo-wide STRICT TestX remains non-pass after GEO-0 due pre-existing non-GEO failures across control, net, ROI, materials, performance, system, and baseline-hash suites. GEO-specific tests introduced in GEO-0 pass.

## 9) Gate Notes

- RepoX STRICT is expected to pass once final GEO artifacts are committed and worktree hygiene clears.
- Full repo-wide STRICT TestX was executed in sharded form and still reported unrelated failures not introduced by GEO-0.
- During final gate preparation, deterministic registry-compile hygiene also required:
  - adding base dimension `CU` to `data/registries/base_dimension_registry.json`
  - aligning arbitration policy schema enums with checked-in registered modes

## 10) Readiness for GEO-1

GEO-0 is ready to support GEO-1 spatial indexing and stable-ID work because:

- topology, metric, partition, and projection contracts are now explicit
- baseline registries provide portable universe definitions across flat, periodic, atlas, identified, and higher-dimensional stubs
- domain integrations have a single deterministic kernel surface to target
- enforcement now detects reintroduction of ad hoc geometry assumptions

Deferred beyond GEO-0:

- world generation content
- pathfinding policy and routing
- geometry editing and mutation authoring
- richer geodesic solvers and non-stub curved-space implementations
