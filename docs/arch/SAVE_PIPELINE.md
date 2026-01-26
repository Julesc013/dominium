# Save Pipeline (SAVE0)

Status: binding.
Scope: save/snapshot/replay capture pipeline and crash safety.

## Purpose
Make saving a first-class, deterministic pipeline with explicit states,
mod participation, and crash-safe commits.

## State machine (explicit)
```
IDLE -> BARRIER -> CAPTURE -> TRANSFORM -> WRITE -> COMMIT -> DONE
                                     \-> FAILED
```

State definitions:
- IDLE: no save in progress.
- BARRIER: freeze authoritative commit boundary (deterministic).
- CAPTURE: snapshot authoritative state via existing snapshot interfaces.
- TRANSFORM: deterministic normalization, ordering, and hashing.
- WRITE: write to staging location (never overwrite last known good).
- COMMIT: atomic promote to new save head.
- DONE/FAILED: terminal state with explicit refusal payload on failure.

## Deterministic boundaries
- Capture ONLY at deterministic commit boundaries (ACT-stable).
- No partial or mid-step snapshots.
- Parallel capture MUST reduce deterministically (ordered reductions).

## Snapshot interfaces
- Reuse existing snapshot interfaces and schemas.
- Snapshot outputs are pure data, no executable logic.
- Unknown extension fields must be preserved.

## Mod participation
- Mods participate via registered save ops.
- Each mod contributes isolated chunks.
- A mod chunk failure MUST NOT corrupt the save; mark refusal for that chunk.
- Missing mod chunks result in explicit degraded/frozen modes on load.

## Backend abstraction
- Storage backend is an interface; no hardcoded paths.
- Saves reference pack/capability lockfiles by hash, not by file path.
- All outputs are deterministic and self-describing.

## Crash safety guarantees
- Never overwrite the last known good save.
- Writes are staged and committed atomically.
- Crash during WRITE or COMMIT leaves last good save intact.

## Refusal semantics
Save failures MUST emit refusal objects with stable codes and payloads.
No silent fallback is allowed.

## See also
- `docs/arch/CONTENT_AND_STORAGE_MODEL.md`
- `docs/arch/REFUSAL_SEMANTICS.md`
- `schema/save_and_replay.schema`
- `schema/snapshot.schema`
