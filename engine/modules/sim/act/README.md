# SIM/ACT (Intents, Actions, Deltas)

Scaffolding for the intent → action → delta pipeline.

## Responsibilities
- Define boundaries: validation vs application.
- Ensure all state mutation occurs via deltas applied at commit points.
- Support deterministic command streams for replay/lockstep.

## Non-responsibilities / prohibited
- No direct mutation of engine state outside deltas.
- No UI/tools writing into SIM state directly.

## Spec
See `docs/specs/SPEC_ACTIONS.md`, `docs/specs/SPEC_PACKETS.md`, and `docs/specs/SPEC_SIM_SCHEDULER.md`.

