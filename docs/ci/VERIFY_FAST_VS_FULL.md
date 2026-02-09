Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Verify Fast vs Full

## `verify_fast`

Purpose: bounded developer feedback.

Includes:
- Repo hygiene/build checks:
  - `all_quality_gates`
  - `check_arch`
  - `check_abi_boundaries`
  - `check_ui_shell_purity`
- UI bind freshness (`ui_bind_phase` on Windows)
- bounded CTest labels: `smoke|portability|buildmeta`
- app/tool smoke probe (`tools/ci/smoke_run_apps.py`)

Target:

```
cmake --build <build-dir> --config <cfg> --target verify_fast
```

Expected runtime band:
- local dev: 30-120 seconds
- CI: 60-180 seconds

## `verify_full`

Purpose: full pre-merge or release validation.

Includes:
- everything in `verify_fast`
- full TestX gate (`testx_all`)

Target:

```
cmake --build <build-dir> --config <cfg> --target verify_full
```

Expected runtime band:
- local dev: 5-25 minutes
- CI: 8-30 minutes

## Release requirement

`dist_all` is release-lane only and must be run after `verify_full` passes.
