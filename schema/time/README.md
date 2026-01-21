--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses time schema for observer clocks and perception policies.
SCHEMA:
- Canonical observer clock, dilation, and buffering formats.
TOOLS:
- Inspection and replay tooling for time perception.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Time Schema (TIME2)

This folder defines the canonical model for observer clocks and time
perception without altering authoritative ACT.

See:
- `SPEC_OBSERVER_CLOCKS.md`
- `SPEC_TIME_DILATION.md`
- `SPEC_PERCEPTION_BUFFERS.md`
