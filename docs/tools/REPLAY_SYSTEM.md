# REPLAY SYSTEM

Replays MUST be deterministic event histories sufficient to reconstruct state.
Replays MUST be distinct from saves; saves are state snapshots.
Replay tooling MUST support load, step, pause/resume, and diff operations.
Replays MUST reference packs by ID, never by path.
Replay tooling MUST be read-only and headless-safe.

References:
- docs/architecture/INVARIANTS.md
- docs/architecture/REALITY_LAYER.md
