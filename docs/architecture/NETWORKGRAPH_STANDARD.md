Status: DERIVED
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: ABS-2 NetworkGraph payload typing, routing, partition hooks, inspection, and visualization standards.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# NetworkGraph Standard

## 1) Payload Typing
- `NetworkGraph` nodes/edges are typed by `node_type_schema_id` and `edge_type_schema_id`.
- `payload_schema_versions` maps schema IDs to semantic versions.
- Node/edge payloads support:
  - inline typed payload (`payload`)
  - external payload reference (`payload_ref`)
- Validation mode is policy-driven:
  - `strict`: schema IDs and versions must be declared
  - `warn`: preserve and continue with diagnostics
  - `off`: skip payload typing checks

## 2) Deterministic Ordering
- Node canonical order: `node_id` ascending.
- Edge canonical order: `(from_node_id,to_node_id,edge_id)` ascending.
- Route tie-break order: lexicographically smallest `edge_id` sequence for equal cost paths.

## 3) Routing Semantics
- Route query inputs:
  - `graph_id`
  - `from_node_id`
  - `to_node_id`
  - `route_policy_id`
  - optional deterministic `constraints`
- Route result outputs:
  - `path_node_ids` ordered
  - `path_edge_ids` ordered
  - `total_cost` (fixed-point compatible integer)
  - `deterministic_fingerprint`
- Baseline policies:
  - `route.direct_only`
  - `route.shortest_delay`
  - `route.min_cost_units`
- Capacity-aware constraints are generic and deterministic; refusal codes:
  - `refusal.route.not_found`
  - `refusal.route.capacity_insufficient`

## 4) Generic Edge Scalars
`NetworkEdge` supports optional generic scalars:
- `capacity`
- `delay_ticks`
- `loss_fraction`
- `cost_units`

These fields are generic substrate controls and not domain-specific gameplay logic.

## 5) Partitioning Hooks (SRZ-Ready)
- `graph_partition` declares shard ownership metadata for nodes/edges.
- Routing can emit deterministic cross-shard route plans:
  - shard-local segments
  - boundary transitions
  - deterministic segment ordering
- This is structural planning only; no distributed execution semantics are introduced here.

## 6) Inspection Hooks
NetworkGraph inspection sections:
- `section.networkgraph.summary`
- `section.networkgraph.route`
- `section.networkgraph.capacity_utilization`

Inspection remains derived-only and epistemic-policy gated.

## 7) Visualization Hooks
- RenderModel overlay may project:
  - node glyphs
  - directed edge lines
  - optional route highlights
- Overlays are derived from Perceived/inspection artifacts only.
- Render path must not access or mutate TruthModel.

## 8) Anti-Duplication Rule
- New bespoke routing/pathfinding engines outside `src/core/graph` are forbidden.
- Domain modules must wrap core graph/routing abstractions instead of re-implementing path logic.

## 9) Migration Guidance
- MAT logistics remains semantically unchanged while consuming `routing_engine` APIs.
- Upcoming INT/MOB/utility/signal systems must bind to `NetworkGraph` + `FlowSystem` instead of creating parallel substrates.
