# SPEC TRAVEL QUEUEING (TRAVEL1)

Status: draft.
Version: 1.0
Scope: deterministic queueing and congestion semantics.

## Queueing Rules
If capacity is unavailable:
- request enters queue
- queue order is deterministic
- dequeue occurs on capacity refill

Queue types:
- FIFO
- priority-based (deterministic ordering key)

## Starvation Rules
No starvation unless explicitly configured and documented.

## Outcomes
- TRAVEL_QUEUE
- TRAVEL_DEFER (with next_due_tick)
- TRAVEL_REFUSE (with reason)

## Determinism Rules
- Queue ordering must be stable across runs.
- No random reordering.
- Admission and dequeue are auditable.

## Integration Points
- TRAVEL0 denial/deferral semantics
- Capacity refill rules (TRAVEL1 capacity)
