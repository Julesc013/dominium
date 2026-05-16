# AIDE-GATE-02 Blockers

## Blocking Issues

None for `AIDE-MOVE-01-APPLY`.

## Non-Blocking Warnings

- The reference plan has high raw reference complexity because generated AIDE/repo evidence and historical audit artifacts mention `ide/README.md`.
- Generated architecture registry references are marked review/regeneration and must not be blindly rewritten.
- The original AIDE-MOVE-01 plan remains draft, not approved, and no-apply. Authorization is represented by the AIDE-GATE-02 report.

## Deferred Risks

- `ide/manifests/**` remains deferred and untouched.
- All other root move waves remain unauthorized.
- Full eval, full CTest, CMake configure/build, package/release generation, and product binaries remain outside this gate.

## Apply Authorization

`AIDE-MOVE-01-APPLY` may proceed for the single planned move only:

`ide/README.md -> docs/architecture/IDE_PROJECTIONS.md`

No other move, delete, rename, reference rewrite, path alias, shim, salvage map, move map, or exception retirement is authorized by this gate.
