Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

## GEO-6 Pathing And Traversal Model

### Purpose

GEO-6 freezes a deterministic, topology-portable traversal substrate over GEO cell graphs.

The substrate must work across:

- `Z^D` grids
- torus wrap worlds
- sphere atlas tiles
- portal-identified spaces
- higher-dimensional stubs

Traversal is derived from explicit GEO contracts rather than domain-local coordinate logic.

### A. Path Query Inputs

Canonical path inputs are:

- `start_ref`
  - either a `geo_cell_key` or a `position_ref`
- `goal_ref`
  - either a `geo_cell_key` or a `position_ref`
- `topology_profile_id`
- `metric_profile_id`
- `partition_profile_id`
- `traversal_policy_id`
- `max_expansions`
- `tier_mode`

`tier_mode` values:

- `macro`
- `meso`
- `micro`

Bounded search is mandatory. A path query that exceeds policy budget must return an explicit bounded partial result or an explicit refusal, never an unbounded search.

### B. Cost Components

Base traversal cost is geometry-derived:

- `base_cost = geo_distance(current_cell, neighbor_cell)`

Optional additive or multiplicative policy-driven modifiers:

- field cost
  - slope
  - hazard
  - pollution
- infrastructure preference
  - roads
  - rails
  - other overlay lanes
- portal cost
  - explicit traversal penalty or preference for identified-edge transitions

Cost composition rules must remain deterministic and profile-driven. No hidden heuristics or runtime-only shortcuts are allowed.

### C. Deterministic Tie-Breaking

Deterministic A* ordering is mandatory.

If candidate nodes have equal `f_score`, GEO-6 must prefer:

1. lower `f_score`
2. lower `g_score`
3. lower canonical `geo_cell_key` ordering

Canonical `geo_cell_key` ordering is:

- `chart_id`
- `index_tuple`
- `refinement_level`

Open-set ordering, closed-set insertion order, and predecessor selection must be stable across runs and platforms.

### D. Tiered Routing

GEO-6 supports tiered traversal without mode flags.

`macro`

- operates on coarser refinement levels
- suitable for long-range movement or dispatch planning

`meso`

- operates on current partition cells
- suitable for ordinary world routing

`micro`

- local navigation stub
- accepts `position_ref` inputs
- may project through current partition cells while preserving deterministic refinement rules

Tier choice is explicit in the request or policy. It is not inferred from hidden runtime state.

### E. Shard Routing

Cross-shard routing is expressed as staged route plans:

- local shard segment
- boundary hop
- remote shard segment

Shard ownership is resolved by `geo_cell_key` assignment or range policy.

Shard routing rules:

- no direct remote shard reads during local segment expansion
- boundary hops are explicit route artifacts
- staged plans must be deterministic for identical inputs

### F. Infrastructure And Overlay Integration

Infrastructure is an optional overlay, not the traversal substrate itself.

Examples:

- roads can reduce cost
- rails can reduce cost or constrain allowed moves
- portals can expose extra legal neighbors

If an overlay is absent, traversal remains valid through base GEO topology and metric rules.

### G. Cache And Replay

Path results are cacheable by:

`H(topology_profile_id, metric_profile_id, partition_profile_id, traversal_policy_id, normalized_request, version)`

Deterministic cache rules:

- stable key derivation
- deterministic eviction order
- cache may be disabled in reference mode for purity verification

Replay must regenerate identical path results and identical fingerprints from the same request, policy, and registry state.

### H. Commitment Surface

`path_result` is derived by default.

When a route is adopted for PROC, SYS, MOB, or LOGIC planning, the engine may emit a canonical plan artifact referencing:

- request hash
- policy hash
- route fingerprint
- shard-stage plan

This preserves replayability without allowing ad hoc recomputation drift.

### I. Non-Goals

GEO-6 does not implement:

- vehicle dynamics
- orbital motion
- hidden runtime heuristics
- wall-clock-dependent timeouts
- non-deterministic best-effort search
