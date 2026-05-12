# SPEC OBSERVER CLOCKS (TIME2)

Status: draft.
Version: 1.0
Scope: observer clock definitions and constraints.

## Definition
Observer clocks map ACT to perceived time for a specific observer.

Required fields:
- observer_id
- clock_id
- dilation_factor (>= 0)
- offset
- buffering_window
- max_lead
- max_lag

Observer clocks are:
- derived
- non-authoritative
- local to an observer or session

## Determinism Rules
- Clock evaluation is deterministic given identical inputs.
- No ACT modification or authoritative scheduling changes.
- No backward jumps unless explicitly in replay mode.

## Integration Points
- TIME2 perception policies
- Law/capability constraints for dilation limits
- Tooling and replay views
