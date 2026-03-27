Status: DERIVED
Last Reviewed: 2026-03-28
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5 bounded src-removal execution against approved mapping lock

# XI-5A Preflight Disaster Cleanup Fix

## Repair Applied

The bounded cleanup repair was applied in [disaster_suite_common.py](/d:/Projects/Dominium/dominium/tools/mvp/disaster_suite_common.py):

1. add `_remove_readonly()` so recursive deletion can clear Windows read-only file attributes before retrying the filesystem operation
2. add `_normalize_tree_permissions()` so staged fixture trees are chmod-normalized before deletion
3. add `_prune_python_bytecode()` so generated `.pyc`/`.pyo` files and `__pycache__` directories are removed before full tree teardown
4. update `_safe_rmtree()` to use bounded deterministic retry-by-iteration cleanup with no wall-clock sleep and no silent failure

This preserves STRICT intent:

- cleanup still hard-fails if the bounded retries cannot remove the tree
- no disaster case assertions were skipped
- no arch-audit checks were weakened

## Validation After Repair

- focused TestX cleanup checks: `pass`
- `validate --all FAST`: `complete`
- `validate --all STRICT`: `complete`

## Files In Scope

- `tools/mvp/disaster_suite_common.py`
- `tools/xstack/testx/tests/test_disaster_harness_reuses_output_root.py`
- `tools/xstack/testx/tests/test_disaster_cleanup_removes_readonly_bytecode.py`
- `data/audit/validation_report_FAST.json`
- `docs/audit/VALIDATION_REPORT_FAST.md`
- `data/audit/validation_report_STRICT.json`
- `docs/audit/VALIDATION_REPORT_STRICT.md`
- `data/audit/xi5a_preflight_repair.json`
- `docs/audit/XI_5A_PREFLIGHT_REPAIR.md`
- `docs/audit/XI_5A_PREFLIGHT_REPAIR_FINAL.md`
