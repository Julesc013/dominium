# POST-CONVERGE-10J Validation

## Focused RepoX

| Command | Result | Notes |
| --- | --- | --- |
| `ctest --preset verify -N` | PASS_WITH_WARNING | Canonical `verify` preset discovers 0 tests in `out/build/vs2026/verify`. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | PASS_WITH_WARNING | No matching tests found because canonical preset discovery is empty. |
| `python scripts/ci/check_repox_rules.py --repo-root . --proof-manifest-out .dominium.local/ctest/repox/proof_manifest_10j_before.json --profile-out .dominium.local/ctest/repox/REPOX_PROFILE_10j_before.json` | FAIL_EXPECTED | Before remediation: 71 failures / 5 warnings. |
| `python scripts/ci/check_repox_rules.py --repo-root . --proof-manifest-out .dominium.local/ctest/repox/proof_manifest_10j_after2.json --profile-out .dominium.local/ctest/repox/REPOX_PROFILE_10j_after2.json` | FAIL_EXPECTED | After remediation: 60 failures / 5 warnings. |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | FAIL_EXPECTED | Tuple-focused CTest remains failing with 60 RepoX failures / 5 warnings. |

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | Passed after restoring required task/review packet sections. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Passed after restoring required packet sections. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Passed; generated `tools/migration/*` metadata side effects were restored because they are outside scope. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest committed message passed; final post-commit check still required after this task commit. |

## Strict Validators

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known `tomllib` fallback warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known `tomllib` fallback warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known `tomllib` fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known `tomllib` fallback warning. |

## Supplemental

| Command | Result | Notes |
| --- | --- | --- |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | `Docs sanity OK.` |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | `BOUNDARY-OK: build boundary checks passed`. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | `UI shell purity OK.` |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | `ABI boundary check OK.` |

## Parsing And Git

| Command | Result | Notes |
| --- | --- | --- |
| JSON parse for `.aide/reports/POST-CONVERGE-10J-authority-doc-findings.json` and `.aide/reports/POST-CONVERGE-10J-repox-before-after.json` | PASS | Both JSON files parse. |
| `git diff --check` | PASS | Passed after removing a trailing blank line from the 10I follow-up note. |
| `git diff --cached --check` | PASS | No staged whitespace issues. |

## Not Run

- Full CTest: not run because focused tuple `inv_repox_rules` remains a semantic blocker.
- CMake configure/build: not run because only documentation metadata, canon index, and evidence/status files changed.
- Product boot proof, portable projection proof, package/release generation, product binaries: not run by scope.
