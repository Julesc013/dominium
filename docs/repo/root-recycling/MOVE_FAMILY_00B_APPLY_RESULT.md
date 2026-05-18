Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00B Apply Result

## Status

- Task: `MOVE-FAMILY-00B-APPLY`
- Result: PASS_WITH_WARNINGS
- Baseline: `BASELINE-00`
- Gate: `MOVE-FAMILY-00B-GATE`
- Apply scope consumed: three tracked IDE manifest files only

## Scope

This apply moved the approved projection manifest schema/examples from `ide/manifests/**` to `contracts/projection/ide/**`, applied the five approved current-reference rewrites, and retired the `ide` source-layout exception after tracked `ide/` state became empty.

No other root family move, feature work, product behavior change, release generation, package generation, build generation, or public release action was performed.

## Moves Applied

| Source | Target |
| --- | --- |
| `ide/manifests/projection_manifest.schema.json` | `contracts/projection/ide/projection_manifest.schema.json` |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | `contracts/projection/ide/examples/example_linux_clang_modern_client_gui.projection.json` |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | `contracts/projection/ide/examples/example_win_vc6_win9x_client_gui.projection.json` |

## Reference Rewrites

Applied only the approved rewrite groups:

- `.gitignore`
- `scripts/verify_docs_sanity.py`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/IDE_PROJECTIONS.md`

Historical, generated, review, and later rewrite groups remain preserved.

## Exception Update

`git ls-files ide` is empty. The empty `ide/` directory tree left by the move was removed after verifying it contained no files. The `ide_root` layout exception is retired in `contracts/repo/layout_exceptions.toml`.

## IDE Root Status

- Tracked `ide/` files: none.
- Filesystem `ide/` path: absent after empty directory cleanup.
- Generated IDE projection output remains ignored if regenerated later.

## Validation

Validation passed with warnings:

- AIDE doctor/validate/test/selftest/tools/roots/repo and commit check passed.
- Strict repo/root/distribution/component validators passed with known TOML fallback-parser warnings.
- Docs sanity, build target boundaries, UI shell purity, and ABI checks passed.
- Focused RepoX passed after adding required four-line status headers to touched planning docs.
- Moved manifest JSON files parsed and examples passed schema-required field checks.

## Rollback

Rollback requires explicit approval and must reverse the three moves, five reference rewrite groups, and `ide_root` exception retirement, then rerun the validation set.

## Next Task

```text
MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof
```

## MOVE-FAMILY-00B-PROOF Result

MOVE-FAMILY-00B-PROOF verified the apply result.

- `git ls-files ide`: empty.
- Filesystem `ide/`: absent.
- `ide_root` exception: retired and accepted by strict validators.
- Moved manifest files under `contracts/projection/ide/**`: tracked, present, JSON parse PASS.
- Old-path active source/tool/validator blockers: none.
- Remaining old-path references: historical, planning, audit, AIDE evidence, root-recycling history, or generated-output references only.
- Next recommended task: `MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan`.
