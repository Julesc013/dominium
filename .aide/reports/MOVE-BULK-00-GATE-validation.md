# MOVE-BULK-00-GATE Validation

## Result

PASS_WITH_WARNINGS.

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | Final doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Latest task/review packets passed required-section checks. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE Lite test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE Lite selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest existing commit check passed before this gate commit. |

## Plan Parsing

| Check | Result | Notes |
| --- | --- | --- |
| MOVE-BULK refactor/gate JSON parsing | PASS | Parsed 20 JSON artifacts. |
| MOVE-BULK TOML inspection | WARN | Local Python lacks `tomllib`/`tomli`; manual required-field inspection passed. |

## Strict Validators

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS | Known TOML fallback warnings; strict result passed. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS | Known TOML fallback warnings; strict result passed. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | Known TOML fallback warning; strict result passed. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | Known TOML fallback warning; strict result passed. |

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
| `git status --short --branch` | PASS | Shows only scoped gate evidence/docs/status changes after validator side effects were cleared. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |

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

- Batch authorization is intentionally partial: Batch A only.
- Batches B-G remain deferred; Batch H remains blocked.
- TOML parser modules are unavailable locally, so TOML was manually inspected.
- Strict validators emit known TOML fallback parser warnings.
- Strict validators updated `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` timestamps/HEAD fields as a side effect; those generated changes were reverted before staging because this is a gate-only task.
