# SPEC BUFFERED PERCEPTION (TIME3)

Status: draft.
Version: 1.0
Scope: read-only buffered perception windows into authoritative history.

## Perception Buffer
A perception buffer is a derived window into ACT history.

Fields:
- observer_id
- buffer_start_ACT
- buffer_end_ACT
- resolution (full | degraded)
- allowed_information_classes

## Rules
- Buffers never expose future ACT beyond permissions.
- Buffers are read-only unless authority permits.
- Buffer windows are bounded by law and capability.

## Determinism Rules
- Buffer selection is deterministic given inputs.
- Clamp behavior is explicit and auditable.

## Integration Points
- TIME2 observer clocks and dilation
- Law/capability constraints
- Epistemic and fog-of-war gates
