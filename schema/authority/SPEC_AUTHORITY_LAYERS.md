# SPEC AUTHORITY LAYERS (OMNI0)

Status: draft.
Version: 1.0
Scope: canonical authority layers and separation rules.

## Authority Layers
Authority is decomposed into independent layers:
- SIMULATION (authoritative state mutation)
- TEMPORAL (time perception and scheduling)
- SPATIAL (movement and boundaries)
- EPISTEMIC (information access)
- GOVERNANCE (law and jurisdiction modification)
- EXECUTION (backend, budgets, determinism policy)
- INTEGRITY (validation, anti-cheat)
- ARCHIVAL (history, freeze, fork)

No layer implies another.

## Determinism Rules
- Capabilities are additive and explicit.
- Absence of capability is not denial.
- Denial must be explicit (negative capabilities).

## Integration Points
- Law gating (schema/law)
- Domain scoping (DOMAIN*)
- Time windows (TIME*)
