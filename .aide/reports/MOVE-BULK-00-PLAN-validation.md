# MOVE-BULK-00-PLAN Validation

## Result

PASS_WITH_WARNINGS.

The AIDE latest task/review packets initially failed validation after refresh because required compact-packet sections were missing. The packets were corrected in scope, then AIDE `validate` and `doctor` passed.

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | WARN then PASS | Initial run failed with `validation should be run`; final rerun passed after validation correction. |
| `py -3 .aide/scripts/aide_lite.py validate` | WARN then PASS | Initial run failed on missing latest task/review packet sections; rerun passed after scoped packet fix. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE Lite test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE Lite selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest existing commit check passed. |

## Plan Parsing

| Check | Result | Notes |
| --- | --- | --- |
| MOVE-BULK JSON parsing | PASS | Parsed 18 JSON artifacts. |
| MOVE-BULK TOML parsing | WARN | Local Python lacks `tomllib` and `tomli`; manual required-field inspection passed for `.aide/refactors/MOVE-BULK-00.global_plan.toml`. |

## Strict Validators

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS | Known TOML fallback parser warnings; strict result passed. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS | Known TOML fallback parser warnings; strict result passed. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | Known TOML fallback parser warning; strict result passed. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | Known TOML fallback parser warning; strict result passed. |

## Supplemental Validators

| Command | Result |
| --- | --- |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS |

## Git Checks

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Shows only scoped planning/docs/report changes after validator side effects were cleared. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |
| `git ls-files ide` | PASS | Empty; `ide/` remains retired. |

## Not Run

- full eval
- full CTest
- CMake configure/build
- package/release generation
- product binaries
- projection regeneration
- move/apply commands
- unknown XStack/AuditX/RepoX/TestX execution

## Known Warnings

- Local Python has no TOML parser module; TOML was manually inspected for required fields.
- Strict validators emit known TOML fallback parser warnings.
- AIDE packet validation initially failed and was corrected before final validation.
- Validator side effects to `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` were detected and reverted before staging because this is a planning-only task.
- The first MOVE-BULK-00 commit passed Git but failed the latest AIDE commit-message check because it omitted the newer `## Changelog` section and `AIDE-Token-Impact` trailer. The task forbids amend/rebase, so this report records the issue and a narrow follow-up commit is used to make the latest commit policy-compliant.
