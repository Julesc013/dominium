# AIDE-MOVE-01 Apply Result

## Status

AIDE-MOVE-01-APPLY completed with warnings and committed a single docs-only move.

## Scope

The authorized scope was only `ide/README.md` to `docs/architecture/IDE_PROJECTIONS.md`. No other move wave was started.

## Move Applied

`ide/README.md` was moved to `docs/architecture/IDE_PROJECTIONS.md`.

## Reference Rewrites

The six planned apply-phase rewrites were applied in `.gitignore`, `scripts/verify_docs_sanity.py`, `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`, the moved document, and `tools/aide/select_move_wave.py`.

## Deferred Material

`ide/manifests/**` remains deferred and untouched. Generated architecture registry and graph references remain review/regeneration items.

## Validation

AIDE doctor/validate/test/selftest/tools/roots/repo checks, strict repo/root/distribution/component validators, docs sanity, build target boundary, UI shell purity, ABI boundary, stale reference search, and git diff checks passed. Python strict validators emitted non-blocking `tomllib` fallback warnings.

## Rollback

Rollback instructions are recorded in `.aide/reports/AIDE-MOVE-01-APPLY-rollback.md`.

## Remaining Root Exception Status

The `ide/` root still exists because `ide/manifests/**` remains. The root exception was not retired.

## Next Task

`AIDE-GATE-03 - Post-Move Proof and Next Wave Readiness Gate`.
