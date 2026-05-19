# Sync Report

## Method

Targeted `.aide/` sync from extracted source pack with preservation filters.

## Results

- Added: 423 portable source files.
- Updated: 16 existing portable source files.
- Unchanged: 136 files.
- Skipped protected target files: 4.
- Checksum failures: 0.

## Updated Existing Files

- `.aide/scripts/aide_lite.py`
- `.aide/scripts/tests/test_cache_local_state.py`
- `.aide/scripts/tests/test_export_import.py`
- `.aide/scripts/tests/test_gateway_commands.py`
- `.aide/scripts/tests/test_golden_tasks.py`
- `.aide/scripts/tests/test_outcome_controller.py`
- `.aide/scripts/tests/test_router_profile.py`
- `.aide/scripts/tests/test_token_ledger.py`
- `.aide/evals/golden-tasks/catalog.yaml`
- `.aide/evals/golden-tasks/changelog_preview_golden/acceptance.md`
- `.aide/evals/golden-tasks/changelog_preview_golden/task.yaml`
- `.aide/commands/catalog.yaml`
- `.aide/context/ignore.yaml`
- `.aide/context/priority.yaml`
- `.aide/policies/export-import.yaml`
- `.aide/policies/token-budget.yaml`

## Skipped / Preserved

- `.aide/memory/**`
- `.aide/queue/**` except Q50 packet
- `.aide/context/dominium-doctrine-refs.md`
- `.aide/context/latest-*` until regenerated locally
- `.aide/reports/dominium-*`
- generated latest reports and inventories until regenerated locally
- `.aide.local/**`

## Conflicts

- Direct import dry-run failed because of a missing `.aide.local.example/secrets/README.md` checksum entry.
- Source expected `.aide/providers/README.md`; the archive did not include it.
- Root `core/gateway/**` and `core/providers/**` were not copied because they are outside Q50 allowed writes.

