# SPEC HYPERSPACE (TRAVEL2)

Status: draft.
Version: 1.0
Scope: hyperspace travel as explicit edges.

## Hyperspace Edge
Traversal mode: HYPERSPACE or JUMP_GATE

Required fields:
- edge_id
- source_node_id
- target_node_id
- traversal_time (explicit)
- capacity and cost (TRAVEL1)
- law/capability constraints
- refinement hooks on arrival

## Notes
Hyperspace corridors are explicit edges, not implied connectivity.
Traversal time may be zero only if declared.

## Integration Points
- DOMAIN permissions along path
- VISITABILITY checks at arrival
- SHARDING cross-shard ordering
