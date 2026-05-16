# AIDE-GATE-03 Blockers

## Blocking Issues

None.

## Non-Blocking Warnings

- Local and remote are equal at the AIDE-MOVE-01-APPLY commit. This is accepted by the revised gate prompt.
- Historical/audit/generated references to the old README path remain and are intentionally preserved.
- `ide/` remains transitional because `ide/manifests/**` remains deferred.
- Strict validators run through `python` emit non-blocking `tomllib` fallback warnings.
- Strict validators temporarily rewrote generated migration metadata headers. The changes were timestamp/SHA-only and were removed from the worktree because this gate cannot write `tools/migration/**`.
- Full eval, full CTest, CMake configure/build, package/release generation, and product binaries remain out of scope.

## Deferred Risks

- Generated architecture registry and graph references should be handled only by a future explicit regeneration/review task.
- `ide/manifests/**` requires a separate future plan before any movement or exception retirement.

## Authorization

AIDE-MOVE-02-PLAN may proceed. Move application remains unauthorized.
