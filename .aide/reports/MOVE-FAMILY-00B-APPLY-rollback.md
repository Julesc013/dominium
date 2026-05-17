# MOVE-FAMILY-00B-APPLY Rollback

## Reverse Moves

If rollback is explicitly approved later, move:

- `contracts/projections/ide/projection_manifest.schema.json` back to `ide/manifests/projection_manifest.schema.json`
- `contracts/projections/ide/examples/example_linux_clang_modern_client_gui.projection.json` back to `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `contracts/projections/ide/examples/example_win_vc6_win9x_client_gui.projection.json` back to `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

## Reverse Reference Rewrites

Restore the five apply rewrite groups:

- `.gitignore`
- `scripts/verify_docs_sanity.py`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/IDE_PROJECTIONS.md`

## Exception Restore

Restore `ide_root` as an active exception in `contracts/repo/layout_exceptions.toml` if tracked files are returned under `ide/`.

## Validation After Rollback

Run:

- AIDE doctor/validate/test/selftest/tools/roots/repo and commit check.
- Strict repo/root/distribution/component validators.
- Docs sanity, build target boundaries, UI shell purity, and ABI checks.
- Focused RepoX.
- `git ls-files ide` and generated-output ignored/staging checks.
