# POST-CONVERGE-10L Validation

Status: DERIVED
Last Reviewed: 2026-05-16

## Focused Reproduction

| Command | Result | Notes |
| --- | --- | --- |
| `ctest --preset verify -N` | PASS | Canonical verify discovery reports 493 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` before | FAIL_EXPECTED | 52 failures / 5 warnings after TEST-PERF-00 and before the 10K audit header fix. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` after | FAIL_EXPECTED | 51 failures / 5 warnings; distribution/product target family remains classified. |

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | No hard validation failures detected. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Passed after review packet path refs avoided ignored distribution wrapper path text. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Internal AIDE checks pass. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Internal AIDE selftest checks pass. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool inventory/wrap-plan validation passes. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root validation passes; generated timestamp churn in `tools/migration/*` was not kept. |
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
| `python -m json.tool .aide/reports/POST-CONVERGE-10L-distribution-product-findings.json` | PASS | JSON parses. |
| `python -m json.tool .aide/reports/POST-CONVERGE-10L-repox-before-after.json` | PASS | JSON parses. |
| JSONL line parse for `.aide/ledgers/migration_ledger.jsonl` | PASS | All non-empty lines parse. |
| `git diff --check` | PASS | No whitespace errors before staging. |

## Not Run

- Full CTest: not run because focused RepoX remains an expected semantic failure.
- Build: not run because POST-CONVERGE-10L changed evidence/status files only.
- Product boot proof, portable projection proof, package proof, and release proof: not run by scope.
