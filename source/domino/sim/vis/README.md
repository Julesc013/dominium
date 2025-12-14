# SIM/VIS (Visibility + Comms)

Derived visibility/occlusion and communications routing scaffolding.

## Responsibilities
- Define deterministic visibility contexts and occlusion models (no floats).
- Route communications/messages deterministically under budget.

## Non-responsibilities / prohibited
- Visibility is never authoritative state; it is derived cache.
- No platform audio/network code; only deterministic message objects.

## Spec
See `docs/SPEC_KNOWLEDGE_VIS_COMMS.md` and `docs/SPEC_DETERMINISM.md`.

