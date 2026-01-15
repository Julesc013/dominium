# SIM/KNOW (Knowledge)

Derived knowledge/belief state scaffolding.

## Responsibilities
- Define interfaces for belief state, memory, and derived knowledge caches.
- Ensure deterministic updates from observations/messages only.

## Non-responsibilities / prohibited
- Knowledge is never authoritative world state; it is derived cache.
- No direct cross-system calls; updates flow via packets/bus.

## Spec
See `docs/SPEC_KNOWLEDGE_VIS_COMMS.md` and `docs/SPEC_DETERMINISM.md`.

