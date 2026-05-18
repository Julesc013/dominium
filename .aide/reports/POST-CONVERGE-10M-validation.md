# POST-CONVERGE-10M Validation

Status: DERIVED
Last Reviewed: 2026-05-16

## Focused Reproduction

| Command | Result | Notes |
| --- | --- | --- |
| `ctest --preset verify -N` | PASS | Canonical verify discovery reports 493 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` before | FAIL_EXPECTED | 51 failures / 5 warnings from POST-CONVERGE-10L baseline. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` after stale path fixes | FAIL_EXPECTED | 23 failures / 5 warnings. |
| `DOM_WS_ID=post-converge-10m-fresh ctest --preset verify -R inv_repox_rules --output-on-failure` | FAIL_EXPECTED | Fresh namespace confirmed the same 23 failures / 5 warnings before the cache file-dependency fix. |

## Additional Focused Checks

| Command | Result | Notes |
| --- | --- | --- |
| `python -m py_compile scripts/ci/check_repox_rules.py` | PASS | RepoX check script compiles. |
| MW-4 import traceback probe | FAIL_EXPECTED | `game.domain.embodiment.__getattr__` imports retired `embodiment.*` modules; source fix out of scope. |

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | No hard validation failures detected. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Latest task/review packets are within budget and pass policy checks. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Internal AIDE checks pass. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Internal AIDE selftest checks pass. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool inventory/wrap-plan validation passes. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root validation passes; generated timestamp/head churn in `tools/migration/*` was not kept. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo intelligence validation passes. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Pre-commit latest commit policy check passed. |

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
| `python -m json.tool .aide/reports/POST-CONVERGE-10M-retired-domain-findings.json` | PASS | JSON parses. |
| `python -m json.tool .aide/reports/POST-CONVERGE-10M-repox-before-after.json` | PASS | JSON parses. |
| JSONL line parse for `.aide/ledgers/migration_ledger.jsonl` | PASS | All non-empty lines parse. |
| `git diff --check` | PASS | No whitespace errors before staging. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |

## Not Run

- Full CTest: not run because focused RepoX remains an expected semantic failure.
- Build: not run because POST-CONVERGE-10M changed RepoX governance code and evidence/status files only.
- Product boot proof, portable projection proof, package proof, and release proof: not run by scope.
