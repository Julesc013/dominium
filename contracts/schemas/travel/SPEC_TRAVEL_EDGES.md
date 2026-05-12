# SPEC TRAVEL EDGES (TRAVEL0)

Status: draft.
Version: 1.0
Scope: explicit travel transitions and constraints.

## Travel Edge
A Travel Edge represents a permitted transition between two nodes.

Required fields:
- edge_id (stable)
- source_node_id
- target_node_id
- traversal_time (ACT function or schedule)
- capacity requirements
- constraints (law targets, capabilities)
- refinement requirements (entry/exit)
- cost model (logistics, energy, bandwidth)

No implicit edge exists.

## Exotic Travel
Portals, wormholes, hyperspace, and hyperlanes MUST be edges:
- explicit traversal semantics
- explicit law targets and capability gates
- explicit capacity limits
- explicit denial reasons
Traversal time may be zero but must be scheduled and auditable.

## Determinism Rules
- Edge ordering is stable.
- Constraint evaluation is deterministic.
- No runtime benchmarking or wall-clock use.

## Integration Points
- DOMAIN: edges must respect domain volumes on source/path/target.
- LAW: edge gates are law-targeted.
- VISITABILITY: arrival requires visitability checks and contracts.
