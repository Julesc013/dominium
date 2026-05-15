# AIDE-MOVE-01-PLAN Validation

## Status

Final validation result: PASS.

## Resolved During Validation

- Initial AIDE validation caught missing sections in the latest task/review packets after the planning update. The packets were corrected and the final AIDE sequence passed.
- Strict layout validators refreshed `tools/migration` evidence as a side effect; those out-of-scope generated changes were reverted before final diff checks.

## Results

| Command | Result | Notes |
| --- | --- | --- |
| `Plan JSON parse` | PASS | All AIDE-MOVE-01 JSON files parsed and enforce apply_allowed=false, approval_status=not_approved. |
| `Plan TOML parse` | PASS | .aide/refactors/AIDE-MOVE-01.plan.toml parsed with tomllib and remains no-apply. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | Final run passed after packet schema sections were restored. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Final run passed; latest task/review packets satisfy required sections. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE focused tests passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool recycling validation passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root recycling validation passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo validation passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest committed baseline check passed before this new commit. |
| `py -3 tools/validators/check_repo_layout.py --repo-root . --strict` | PASS | Strict repo layout passed; transitional roots remain excepted. |
| `py -3 tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS | Strict root allowlist passed; no unexcepted violations. |
| `py -3 tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | Distribution layout passed with warnings=0. |
| `py -3 tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | Component matrix passed with warnings=0. |
| `py -3 scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `py -3 scripts/verify_build_target_boundaries.py --repo-root .` | PASS | BOUNDARY-OK. |
| `py -3 scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `py -3 scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors at time of check. |

## Not Run

- Full eval: out of scope for AIDE-MOVE-01-PLAN.
- Full CTest: out of scope for this no-apply planning task.
- CMake configure/build: out of scope.
- Package/release generation: out of scope.
- Product binaries: out of scope.
- Move/apply commands: forbidden by task scope.
