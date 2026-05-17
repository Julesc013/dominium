# MOVE-FAMILY-00B-APPLY Post-State

## Tracked State

- `git ls-files ide`: empty.
- `contracts/projections/ide/projection_manifest.schema.json`: tracked by move.
- `contracts/projections/ide/examples/example_linux_clang_modern_client_gui.projection.json`: tracked by move.
- `contracts/projections/ide/examples/example_win_vc6_win9x_client_gui.projection.json`: tracked by move.

## Filesystem State

Only empty directories remained under `ide/` after `git mv`. The path was verified under the workspace, checked for files, and then the empty directories were removed. `Test-Path ide` is false.

## Exception State

`contracts/repo/layout_exceptions.toml` moved `ide_root` from active exceptions to retired exceptions. Strict repo layout and root allowlist validators pass with active exception count 31.

## Generated Output Policy

Future generated IDE projection output under `ide/**` remains ignored by `.gitignore`. Generated output must not be committed.

## Baseline

RELEASE-00 remains the structural regression baseline. This task did not regenerate release, projection, package, installer, product binary, or build outputs.
