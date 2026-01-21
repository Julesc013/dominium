# SPEC TRAVEL SCHEDULING (TRAVEL0)

Status: draft.
Version: 1.0
Scope: scheduled travel effects on ACT time.

## Scheduling Pipeline
1) Travel Intent
   - "I want to go from A to B"
2) Path Resolution
   - deterministic path selection
   - domain permission validation
3) Law & Capability Gate
   - origin, each edge, destination
4) Budget & Capacity Gate
   - time, logistics, congestion
5) Schedule Effects
   - OP_TRAVEL_BEGIN
   - OP_TRAVEL_PROGRESS (optional)
   - OP_TRAVEL_ARRIVE

## ACT Time Semantics
- Travel consumes ACT time.
- Arrival is a scheduled effect.
- Zero-time edges are still scheduled.

## Determinism Rules
- No implicit movement or hidden transitions.
- Edge traversal time is deterministic given inputs.
- Scheduling order is stable and auditable.

## Integration Points
- EXEC/HWCAPS: budget gating and deterministic deferral.
- DOMAIN4: arrival requires visitability acceptance.
- LAW: admission for travel intent and arrival effects.
