# SPEC TRAVEL LATENCY (TRAVEL1)

Status: draft.
Version: 1.0
Scope: ACT-based latency and traversal time.

## Definition
Latency is the ACT time between OP_TRAVEL_BEGIN and OP_TRAVEL_ARRIVE.

Latency may be:
- constant
- function of load
- function of distance

## Determinism Rules
- Given identical inputs, latency is identical.
- No hidden accelerations or time skips.
- Zero-time edges are allowed but must be scheduled and auditable.

## Integration Points
- TRAVEL0 scheduling pipeline
- Capacity and queueing (TRAVEL1)
