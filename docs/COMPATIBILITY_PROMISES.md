# COMPATIBILITY_PROMISES (FINAL0)

Status: draft  
Version: 1

## Purpose
Define the compatibility promises for saves, replays, and mods.

## Saves
- Saves must never silently break.
- Unsupported schema major versions must refuse or migrate deterministically.
- Save metadata must include schema versions and feature epochs.

## Replays
- Replays must be replayable under pinned versions.
- If required schemas or epochs are missing, replays must refuse.

## Mods
- Mods must refuse or degrade deterministically (see MOD0).
- Sim-affecting incompatible mods must refuse; no silent disable.
- Non-sim mods may be disabled only via explicit safe mode.

## Schema major changes
- Any schema major bump requires a migration or explicit refusal path.
- Changes must be recorded in compatibility notes.

## Prohibitions
- Silent breaking changes.
- Implicit fallback that alters simulation outcomes.
