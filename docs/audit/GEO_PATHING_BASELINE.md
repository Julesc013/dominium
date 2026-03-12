Status: BASELINE
Last Updated: 2026-03-09
Version: 1.0.0
Scope: GEO-6 deterministic pathing, traversal cost composition, shard-stage route planning, and replay proof surfaces.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# GEO Pathing Baseline

## 1) Scope

GEO-6 freezes the geometry-portable traversal substrate on top of:

- GEO-0 topology, metric, partition, and projection constitutions
- GEO-1 stable cell identity
- GEO-2 frame and precision discipline
- GEO-3 deterministic metric and neighborhood queries
- GEO-4 GEO-bound field sampling
- GEO-5 projection and lens separation

The authoritative doctrine is:

- `docs/geo/PATHING_AND_TRAVERSAL_MODEL.md`

Relevant invariants and contracts upheld:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/canon/constitution_v1.md` C1 Version semantics
- `docs/canon/constitution_v1.md` C3 CompatX obligations
- `INV-PATHING-DETERMINISTIC`
- `INV-NO-ADHOC-NEIGHBOR-ENUMERATION`

## 2) Retro Audit Summary

Retro-consistency findings are recorded in `docs/audit/GEO6_RETRO_AUDIT.md`.

The audit confirmed:

- macro mobility routing already existed for authored network graphs but not for GEO cell graphs
- local movement already had some GEO distance usage but no canonical GEO-native route planner
- ROI scheduling had a GEO distance seam but no traversal substrate
- portal, torus, and atlas portability required pathing to move onto GEO neighbors instead of topology-specific code

GEO-6 therefore stayed targeted:

- no vehicle dynamics
- no worldgen content
- no wall-clock control
- no truth mutation from derived route artifacts

## 3) Traversal Policy Baseline

New traversal schemas:

- `schema/geo/traversal_policy.schema`
- `schema/geo/path_request.schema`
- `schema/geo/path_result.schema`

New baseline registry:

- `data/registries/traversal_policy_registry.json`

Frozen traversal policies:

- `traverse.default_walk`
- `traverse.vehicle_stub`
- `traverse.rail_prefer_stub`
- `traverse.portal_allowed_stub`

Each policy now declares:

- allowed neighbor kinds
- cost weights
- infrastructure preference
- bounded `max_expansions`
- deterministic heuristic and partial-result policy metadata in extensions

## 4) Path Runtime Baseline

Core runtime lives in:

- `src/geo/path/path_engine.py`
- `src/geo/path/shard_route_planner.py`

Frozen GEO-6 query surfaces:

- `build_path_request(...)`
- `normalize_path_request(...)`
- `geo_path_query(...)`
- `build_shard_route_plan(...)`
- `resolve_cell_shard_id(...)`
- `path_result_proof_surface(...)`

Key runtime rules:

- path expansion is over `geo_cell_key` graphs only
- neighbors come from `geo_neighbors(...)`
- step cost starts from `geo_distance(...)`
- optional field and infrastructure modifiers remain explicit input hooks
- tie-breaking is stable by:
  - `f_score`
  - `g_score`
  - canonical `geo_cell_key` ordering
- bounded search emits:
  - complete result
  - explicit partial result
  - explicit refusal

## 5) Traversal Policies And Cost Layers

Base cost:

- geometry-derived metric distance between cell centers

Optional cost layers:

- field cost through GEO-bound field sampling payloads
- infrastructure preference through explicit overlay edge records
- portal cost through topology transition classification

Important constraint:

- the heuristic remains safe and deterministic
- when cost modifiers could invalidate admissibility, GEO-6 degrades to a zero heuristic rather than using hidden non-admissible shortcuts

## 6) Deterministic Tie-Breaking

GEO-6 freezes stable open-set ordering through `_best_open_candidate(...)`.

Equal-cost alternatives resolve by canonical cell ordering, which prevents:

- hash-map iteration drift
- platform-dependent queue order
- hidden search instability

The baseline tie-break is verified by `test_astar_deterministic`.

## 7) Shard Route Planning

Cross-shard planning is derived in `src/geo/path/shard_route_planner.py`.

Frozen shard-stage rules:

- shard ownership is resolved from `geo_cell_key`
- routes are segmented into shard-local path segments
- boundary transitions are explicit `boundary_hops`
- the planner never performs direct remote shard reads

This establishes the shard-safe contract GEO-8 worldgen and future SYS/PROC planning can consume.

## 8) Proof And Replay Baseline

Proof and replay surfaces added:

- `tools/geo/tool_replay_path_request.py`
- `path_result_proof_surface(...)`

Proof context now supports:

- `traversal_policy_registry_hash`
- `path_request_hash_chain`
- `path_result_hash_chain`
- `traversal_policy_ids`
- `partition_profile_ids`

Session/global state now records `traversal_policy_registry_hash` so replay and transport proof surfaces can carry the same deterministic traversal registry anchor.

## 9) Enforcement Baseline

RepoX scaffolding added:

- `INV-PATHING-DETERMINISTIC`
- `INV-NO-ADHOC-NEIGHBOR-ENUMERATION`

AuditX analyzers added:

- `E344_NONDETERMINISTIC_PATH_SMELL`
- `E345_ADHOC_HEURISTIC_SMELL`

These checks enforce the presence of:

- canonical GEO path entry points
- deterministic tie-break surfaces
- bounded search metadata
- replay hash tooling
- declared traversal policy heuristic metadata

## 10) Contract And Schema Impact

Changed:

- new traversal schemas and registry
- new GEO path engine and shard planner runtime
- new replay/proof hash surfaces for deterministic path results
- session/global state registry hash recording for traversal policies
- new RepoX/AuditX/TestX enforcement and validation scaffolding

Unchanged:

- process-only mutation invariant
- truth tick ordering
- authored graph routing for existing infrastructure systems
- vehicle dynamics and orbital integration responsibilities
- render/lens truth isolation

## 11) Validation Snapshot

Executed during GEO-6 baseline:

- targeted GEO-6 TestX subset
- replay verifier for deterministic path fixtures
- RepoX/AuditX preflight during implementation
- final strict gates recorded after baseline completion

## 12) Readiness

GEO-6 is ready for:

- GEO-7 geometry editing contracts
- GEO-8 worldgen interface binding

because the repository now has:

- deterministic cell-graph routing
- topology-portable traversal semantics
- shard-stage route plans
- replay-stable path identities and proof hashes
