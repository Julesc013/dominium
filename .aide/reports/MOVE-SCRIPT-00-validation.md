Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# MOVE-SCRIPT-00 Validation

Result: PASS_WITH_WARNINGS.

## Sync And Start State

- `git status --short --branch`: clean at task start.
- `git fetch --all --prune`: PASS.
- `git rev-parse HEAD`: `1612f92fe0f51f761ad5078f099e6343ddfda5ff`.
- `git rev-parse origin/main`: `1612f92fe0f51f761ad5078f099e6343ddfda5ff`.
- Merge-base ancestor checks: PASS both ways before edits.

## Router Validation

- `py -3 -m py_compile tools/migration/route_bad_roots.py`: PASS.
- `python tools/migration/route_bad_roots.py --help`: PASS.
- `python tools/migration/route_bad_roots.py --repo-root . --dry-run --rules tools/migration/bad_root_routing_rules.json --json-out .aide/reports/MOVE-SCRIPT-00-routing-preview.json --md-out .aide/reports/MOVE-SCRIPT-00-routing-preview.md --skipped-out .aide/reports/MOVE-SCRIPT-00-skipped-ledger.json --root-summary-out .aide/reports/MOVE-SCRIPT-00-root-summary.json --batch-plan-out .aide/reports/MOVE-SCRIPT-00-batch-plan.json --fail-on-collision`: PASS_WITH_WARNINGS.
- Same router command with `--fail-on-unknown`: PASS_WITH_WARNINGS.
- JSON parse for routing rules and generated route/skipped/root/batch reports: PASS.

## Dry-Run Summary

- Bad-root tracked files scanned: 1,765.
- Route candidates: 1,593.
- Skipped/deferred: 172.
- Collisions: 0.
- Moves applied: 0.
- Deletes applied: 0.
- Renames applied: 0.
- References rewritten: 0.
- Imports rewritten: 0.
- Shims created: 0.
- Exceptions retired: 0.

## AIDE

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing review-packet warning.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS.

## Strict Validators

- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS with existing TOML fallback warnings.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS with existing TOML fallback warnings.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS with existing TOML fallback warning.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS with existing TOML fallback warning.

## NAME-00 Validators

- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_path_terms.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_directory_naming.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_file_naming.py --repo-root .`: PASS_WITH_WARNINGS.

The NAME-00 warnings are current classified naming debt; this task did not move or rename files.

## Supplemental Checks

- `python scripts/verify_docs_sanity.py --repo-root .`: PASS.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.

## CTest

- `ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300`: PASS, 132.31 seconds.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS, 57 tests, 49.69 seconds.

Full CTest was not run by scope; it remains governed by the TEST-PERF-01 sharded execution policy.

## Generated Churn

Strict layout validation refreshed `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` timestamp/SHA fields. Those generated metadata changes were restored because they are outside MOVE-SCRIPT-00 write scope.
