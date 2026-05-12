# SPEC PORTALS (TRAVEL2)

Status: draft.
Version: 1.0
Scope: portal travel as explicit edges.

## Portal Edge
Traversal mode: PORTAL

Required fields:
- edge_id
- source_node_id
- target_node_id
- traversal_time (may be zero, explicit)
- capacity and cost (TRAVEL1)
- law/capability constraints
- refinement hooks on arrival

## Determinism Rules
- No implicit portals.
- Zero-time is explicit and scheduled.
- Denial reasons are auditable.

## Integration Points
- DOMAIN permissions
- VISITABILITY checks
- SHARDING message ordering
