# SPEC_FEATURE_EPOCH — Feature Epochs (Authoritative Gate)

Feature epochs provide a coarse compatibility gate across formats and
simulation behavior. They are separate from schema versions.

## 1. Definition
- `feature_epoch` is a `u32` value embedded in authoritative containers.
- Epochs are monotonically increasing.
- Epoch `1` is the baseline epoch for current formats.

## 2. Policy
- If `feature_epoch` matches, the container MAY load (subject to schema/version checks).
- If `feature_epoch` differs, a migration path is required.
- If no migration path exists, the load MUST refuse.
- A missing `feature_epoch` field in an authoritative container MUST be treated
  as `MIGRATION_REQUIRED` (not best-effort).

## 3. Affected formats
The following containers carry `feature_epoch`:
- Universe bundle (`docs/SPEC_UNIVERSE_BUNDLE.md`)
- Save (`source/dominium/game/SPEC_SAVE.md`)
- Replay (`source/dominium/game/SPEC_REPLAY.md`)

## 4. Runtime policy hooks
Implementations MUST expose deterministic helpers equivalent to:
- `feature_epoch_current()` → returns the current epoch.
- `feature_epoch_supported(epoch)` → returns true only for supported epochs.
- `feature_epoch_requires_migration(from, to)` → true if a migration is required.

## 5. Relationship to schema versions
- Schema versions track structural changes within an epoch.
- Epoch changes represent broader compatibility shifts that may span multiple schemas.

## Related specs
- `docs/SPEC_MIGRATIONS.md`
- `docs/SPEC_DETERMINISM.md`
