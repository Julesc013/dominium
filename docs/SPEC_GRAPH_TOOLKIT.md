# SPEC_GRAPH_TOOLKIT — Canonical Deterministic Graph Storage

This spec defines canonical storage rules for graphs used in deterministic
simulation (connectivity, adjacency, constraints, stitching, etc.).

## Scope
Applies to:
- canonical node/edge identity and ordering
- adjacency storage and traversal
- incremental dirty rebuild rules
- boundary stitching across partitions/domains

## Canonical graph storage
- Nodes and edges MUST have stable numeric IDs.
- Graph traversal MUST be defined by canonical ordering:
  - adjacency lists stored as arrays sorted by neighbor ID
  - if multiple edge types exist, sort by `(edge_kind, neighbor_id, edge_id)`

Graphs MUST NOT rely on:
- hash-table iteration order
- pointer identity
- memory layout/padding comparisons

## Incremental dirty rebuild rules
- Dirty marking MUST be explicit and deterministic.
- Rebuild work MUST be expressed as work items with stable keys and processed
  under per-tick budgets (`docs/SPEC_SIM_SCHEDULER.md`).
- Carryover MUST preserve canonical ordering (no randomization).

## Boundary stitching
"Stitching" connects graphs across boundaries (domains/frames/tiles/etc.).
Rules:
- boundary endpoints MUST have stable IDs
- stitching order MUST be canonical (sorted by stable key)
- stitch results MUST be deterministic and reproducible from authoritative inputs

## Forbidden behaviors
- Unordered adjacency sets in determinism paths.
- Floating-point coordinates used as keys.
- Tolerance-based geometric stitching (epsilon merges).

## Source of truth vs derived cache
**Source of truth:**
- the underlying authoritative state and/or compiled artifacts that define graph
  connectivity

**Derived cache:**
- adjacency caches and acceleration indices (must be regenerable)
- stitch caches (must be regenerable)

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_LOD.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`
- `docs/SPEC_TRANS_STRUCT_DECOR.md`

