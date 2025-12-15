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
- Graph traversal MUST be defined by canonical ordering (no unordered adjacency):
  - adjacency lists are stored as per-node contiguous arrays
  - adjacency iteration order is **always** sorted by:
    1. `neighbor_node_id` ascending
    2. `edge_id` ascending
  - if multiple edge kinds exist, ordering MUST still be total and stable
    (e.g. `(edge_kind, neighbor_node_id, edge_id)`), with explicit tie-breakers

Graphs MUST NOT rely on:
- hash-table iteration order
- pointer identity
- memory layout/padding comparisons

## Partitioning (chunk-aligned)
Graphs MAY be partitioned into chunk-aligned regions for incremental rebuild.

Rules:
- Partition IDs MUST be stable fixed-size integers (recommended: use the same
  stable `chunk_id` used for SIM budgeting).
- Each partition maintains a canonical node list sorted by `node_id` ascending.
- Node assignment changes MUST update partition node lists deterministically.

## Incremental dirty rebuild rules
- Dirty marking MUST be explicit and deterministic.
- Dirty sets MUST iterate in canonical ascending ID order (no insertion-order
  dependence).
- Rebuild work MUST be expressed as work items with stable keys and processed
  under per-tick budgets (`docs/SPEC_SIM_SCHEDULER.md`).
- Carryover MUST preserve canonical ordering (no randomization).

## Boundary stitching
"Stitching" connects graphs across boundaries (domains/frames/tiles/etc.).
Rules:
- boundary endpoints MUST have stable IDs and a stable boundary key
  (e.g. a quantized coordinate key; no floats)
- stitching order MUST be canonical (sorted by stable key)
- endpoint sorting key MUST be total (no equal-keys ambiguity), e.g.:
  `(boundary_key, partition_id, node_id)` ascending
- edge creation order MUST be canonical and MUST NOT depend on discovery order;
  within each `boundary_key` group, pair/edge enumeration MUST be deterministic
  (e.g. lexicographic pair order over the sorted endpoint list)
- stitch results MUST be deterministic and reproducible from authoritative inputs

## Dirty sets
Dirty sets track:
- dirty nodes (`node_id`)
- dirty edges (`edge_id`)
- dirty partitions (`partition_id`)

Semantics:
- `add`/`remove` operations maintain sorted unique ID arrays
- `merge` is a deterministic set union
- iteration is always canonical ascending by ID

## Rebuild scheduling + budgets
Rebuild work runs during **PH_TOPOLOGY** under scheduler budgets.

Rules:
- Dirty sets are converted into scheduler work items with stable keys
  (`dg_order_key`) and explicit integer work-unit costs.
- Work keys MUST be derived only from stable IDs (graph type/instance, partition,
  node/edge IDs, and explicit sequences when needed).
- Processing MUST stop on the first item that cannot fit in remaining budget
  (no skipping); the remaining suffix carries over unchanged.

## Forbidden behaviors
- Unordered adjacency sets in determinism paths.
- Floating-point coordinates used as keys.
- Tolerance-based geometric stitching (epsilon merges).

## Source of truth vs derived cache
**Source of truth:**
- the underlying authoritative state that defines graph connectivity (authoring
  models + committed deltas + stable IDs)

**Derived cache:**
- compiled adjacency caches and acceleration indices (must be regenerable)
- stitch caches (must be regenerable)

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_LOD.md`
- `docs/SPEC_DOMAINS_FRAMES_PROP.md`
- `docs/SPEC_TRANS_STRUCT_DECOR.md`
