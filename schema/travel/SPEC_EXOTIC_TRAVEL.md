# SPEC EXOTIC TRAVEL (TRAVEL2)

Status: draft.
Version: 1.0
Scope: canonical model for non-classical travel as explicit edges.

## Definition
Exotic travel is any non-classical movement (portal, wormhole, hyperspace,
jump gate). All exotic travel is represented as explicit TravelEdges.

## Exotic Edge Requirements
Each exotic edge declares:
- traversal_mode (PORTAL, WORMHOLE, HYPERSPACE, JUMP_GATE, CUSTOM)
- traversal_time (may be zero, explicit)
- capacity and cost (TRAVEL1)
- constraints (law targets, capabilities)
- refinement hooks (DOMAIN4)

No exotic travel exists outside this structure.

## Zero-Time Rule
Zero-time traversal is allowed only if explicitly declared:
- scheduled and auditable
- capacity-limited unless explicitly infinite
- arrival effects processed deterministically after admission

## Integration Points
- DOMAIN permissions at source/transit/destination
- VISITABILITY checks on arrival
- ARCHIVAL/FORKING rules
- SHARDING cross-shard message ordering
