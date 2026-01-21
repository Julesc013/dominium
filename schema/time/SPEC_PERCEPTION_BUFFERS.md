# SPEC PERCEPTION BUFFERS (TIME2)

Status: draft.
Version: 1.0
Scope: buffered perception and lag windows.

## Definition
Observers may view the world at ACT - delta within bounded windows.

Buffering fields:
- buffering_window
- max_lead
- max_lag

## Rules
- Buffering is read-only unless authority permits.
- No future leakage beyond max_lead.
- Buffered views do not affect authoritative state.

## Determinism Rules
- Buffer resolution is deterministic.
- Clamp behavior is explicit and auditable.

## Integration Points
- Observer clocks (TIME2)
- Law/capability constraints for buffer limits
