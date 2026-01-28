# Travel and Movement (TRAVEL0)

Status: draft.
Scope: canonical movement model across all scales and domains.

## Core Invariants
- All movement is scheduled on ACT.
- No implicit teleportation.
- Exotic travel is an explicit graph edge.
- Reachability and visitability gates apply at arrival.

## Travel Graph Model
Movement is a path over explicit travel nodes and edges:
- nodes define locations or travel states
- edges define allowed transitions and constraints

## Scheduling Pipeline
1) Travel intent
2) Deterministic path resolution
3) Domain permission checks
4) Law and capability gates
5) Budget and capacity gates
6) Scheduled effects (begin/progress/arrive)

## Domain and Law Integration
- Path segments must stay within permitted domain volumes.
- Law targets apply at origin, along edges, and at destination.
- Forbidden volumes block traversal, not just entry.

## Visitability Integration
Arrival requires DOMAIN4 visitability:
- destination must be refinable or realized
- refinement contracts required
- budgeted deferral or degradation allowed

## Denials
Denials are explicit and auditable:
- NO_PATH
- DOMAIN_FORBIDDEN
- LAW_FORBIDDEN
- CAPABILITY_MISSING
- BUDGET_INSUFFICIENT
- DESTINATION_NOT_VISITABLE

## References
- `schema/travel/SPEC_TRAVEL_GRAPH.md`
- `schema/travel/SPEC_TRAVEL_EDGES.md`
- `schema/travel/SPEC_TRAVEL_SCHEDULING.md`
- `schema/travel/SPEC_TRAVEL_DENIAL.md`
- `docs/arch/VISITABILITY_AND_REFINEMENT.md`
- `docs/arch/REALITY_LAYER.md`
