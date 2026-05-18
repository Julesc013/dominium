# POST-CONVERGE-10N Validation

Status: DERIVED
Last Reviewed: 2026-05-17

## Focused Reproduction

| Command | Result | Notes |
| --- | --- | --- |
| `ctest --preset verify -N` | PASS | Canonical verify discovery reports 493 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` before | FAIL_EXPECTED | 23 failures / 5 warnings from POST-CONVERGE-10M baseline. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` after evidence refresh | FAIL_EXPECTED | 20 failures / 5 warnings. |
| `python scripts/ci/check_repox_rules.py --repo-root .` | FAIL_EXPECTED | 20 failures / 5 warnings; refreshed tracked RepoX proof/profile evidence. |

## Additional Focused Checks

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/ci/tool_identity_fingerprint.py --repo-root . --check` | PASS | Identity fingerprint matches generator output. |
| `python tools/xstack/securex/securex.py integrity-manifest --repo-root . --output .dominium.local/securex-integrity-10n-after.json` plus `git diff --no-index` | PASS | Tracked integrity manifest matches generator output. |
| `python -m py_compile scripts/ci/check_repox_rules.py` | PASS | RepoX check script compiles. |

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
| `py -3 .aide/scripts/aide_lite.py commit check --latest` after initial 10N commit | FAIL | Initial 10N implementation commit `e80dc704c` used lowercase changelog bullets instead of the required machine-readable category prefixes. No amend was used; this validation note is recorded in a follow-up commit. |

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
| `python -m json.tool .aide/reports/POST-CONVERGE-10N-tool-audit-findings.json` | PASS | JSON parses. |
| `python -m json.tool .aide/reports/POST-CONVERGE-10N-repox-before-after.json` | PASS | JSON parses. |
| JSONL line parse for `.aide/ledgers/migration_ledger.jsonl` | PASS | All non-empty lines parse. |
| `git diff --check` | PASS | No whitespace errors before staging. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |

## Not Run

- Full CTest: not run because focused RepoX remains an expected semantic failure.
- Build: not run because POST-CONVERGE-10N changed RepoX governance code and evidence/status files only.
- Product boot proof, portable projection proof, package proof, and release proof: not run by scope.
