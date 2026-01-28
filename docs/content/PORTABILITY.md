# Content Portability

Status: draft (implementation gaps noted).
Scope: pack, save, and replay portability rules.
Authority: canonical for required contract; blockers listed below.

## Required contract
- Saves and replays MUST reference pack IDs and version constraints only.
- No file paths or platform-specific locations may appear in saves or replays.
- Unknown fields and tags MUST be preserved for forward compatibility.
- Missing capabilities MUST trigger explicit degradation or refusal.

## Current state (as-is)
- Schema contracts define forward-compatible records.
- Save/replay portability enforcement is not yet audited in engine/game code.

## Blockers to resolve in Phase 6
- Enforce pathless references in save/replay serialization.
- Ensure refusal semantics are explicit and testable.

## References
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/schema/FORWARD_COMPATIBILITY.md`
