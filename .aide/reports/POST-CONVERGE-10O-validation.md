# POST-CONVERGE-10O Validation

Status: DERIVED
Last Reviewed: 2026-05-17

## Focused RepoX

| Command | Result | Notes |
| --- | --- | --- |
| `ctest --preset verify -N` | PASS | Canonical verify discovery reports 493 tests. Output includes missing-executable notices for compiled tests because 10O did not rebuild. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | FAIL_EXPECTED | 20 failures / 5 warnings. Focused RepoX remains the semantic blocker. |

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | No hard validation failures detected. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Latest task/review packets pass policy checks. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Internal AIDE checks pass. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Internal AIDE selftest checks pass. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool inventory/wrap-plan validation passes. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root validation passes; generated timestamp/head churn in `tools/migration/*` was not kept. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo intelligence validation passes. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest pre-10O commit policy check passes. |

## Existing Validators

| Command | Result |
| --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS |

## Supplemental

| Command | Result |
| --- | --- |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS |

## Data And Git

| Command | Result | Notes |
| --- | --- | --- |
| `python -m json.tool .aide/reports/POST-CONVERGE-10O-repox-closeout.json` | PASS | JSON parses. |
| JSONL parse for `.aide/ledgers/migration_ledger.jsonl` | PASS | 31 non-empty lines parse. |
| `git status --short --branch` | PASS | Shows only scoped 10O evidence/status changes before staging. |
| `git diff --check` | PASS | No whitespace errors before staging. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |

## Not Run

- Full CTest: not run because focused RepoX still has hard semantic failures.
- Build: not run because 10O only writes closeout/status evidence.
- Product boot proof, portable projection proof, package proof, and release proof: not run by scope.
