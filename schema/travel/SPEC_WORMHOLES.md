# SPEC WORMHOLES (TRAVEL2)

Status: draft.
Version: 1.0
Scope: wormhole travel as explicit edges.

## Wormhole Edge
Traversal mode: WORMHOLE

Required fields:
- edge_id
- source_node_id
- target_node_id
- traversal_time (explicit; may be zero)
- capacity and cost (TRAVEL1)
- law/capability constraints
- refinement hooks on arrival

## Stability and Denial
Wormholes may be disabled by law or policy:
- denial must be explicit and deterministic
- no silent fallback to teleport

## Integration Points
- DOMAIN permissions
- VISITABILITY checks
- ARCHIVAL/FORKING rules
