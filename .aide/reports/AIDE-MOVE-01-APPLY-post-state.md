# AIDE-MOVE-01-APPLY Post-State

## Paths

- `ide/README.md`: absent after apply.
- `docs/architecture/IDE_PROJECTIONS.md`: present after apply.
- `ide/manifests/**`: present and untouched.

## Root Status

The `ide/` root remains because `ide/manifests/**` is still tracked and deferred, and generated projection outputs may still appear under `ide/`.

## Exception Status

The `.gitignore` README exception was removed. The layout exception ledger was not retired or changed.

## Stale Reference Status

Remaining `ide/README.md` references are limited to:

- root-recycling planning/history docs,
- generated architecture registry/graph review items,
- historical repository audit evidence.

No extra rewrite outside the six planned apply-phase edits was applied.
