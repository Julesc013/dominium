# MOVE-FAMILY-00B-APPLY Status

## Result

PASS_WITH_WARNINGS.

## Scope

MOVE-FAMILY-00B-APPLY consumed the MOVE-FAMILY-00B-GATE authorization and applied only the approved IDE manifest projection migration.

## Moves Applied

| Source | Target | Status |
| --- | --- | --- |
| `ide/manifests/projection_manifest.schema.json` | `contracts/projections/ide/projection_manifest.schema.json` | applied |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | `contracts/projections/ide/examples/example_linux_clang_modern_client_gui.projection.json` | applied |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | `contracts/projections/ide/examples/example_win_vc6_win9x_client_gui.projection.json` | applied |

## Reference Rewrites

Applied the five approved rewrite groups:

- `.gitignore`
- `scripts/verify_docs_sanity.py`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/IDE_PROJECTIONS.md`

No historical, generated, review, or later rewrite group was rewritten.

## IDE Root Status

- `git ls-files ide`: empty.
- `Test-Path ide`: false after removing only empty directories left by the move.
- `ide` source-layout exception: retired in `contracts/repo/layout_exceptions.toml`.
- Active layout exception count: 31.

## Validation

Validation passed with known warnings. Focused RepoX first exposed missing four-line status headers in three touched planning docs; those metadata headers were repaired and focused RepoX reran clean.

## Next

`MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof`.
