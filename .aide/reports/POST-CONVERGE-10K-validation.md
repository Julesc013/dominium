
# POST-CONVERGE-10K Validation

| Command | Result | Notes |
| --- | --- | --- |
| `ctest --preset verify -N` | PASS_WITH_WARNINGS | Exit 0; canonical preset still discovers 0 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | PASS_WITH_WARNINGS | Exit 0 because canonical preset discovers no matching tests. |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | FAIL_EXPECTED | Exit 8; focused tuple RepoX remains failing at 51 failures / 5 warnings. |
| `python scripts/ci/check_repox_rules.py --repo-root .` | FAIL_EXPECTED | Direct RepoX reduced from 59 failures / 5 warnings to 51 failures / 5 warnings. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | Exit 0. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Exit 0. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Exit 0. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Exit 0. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Exit 0. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Exit 0; generated root metadata changes were restored because root inventory refresh is out of scope. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Exit 0. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Exit 0 against pre-10K latest commit. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS | Exit 0. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS | Exit 0. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | Exit 0. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | Exit 0. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Exit 0. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Exit 0. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | Exit 0. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | Exit 0. |
| `python -m json.tool data/registries/semantic_contract_registry.json` | PASS | Exit 0. |
| `semantic contract registry validator` | PASS | Exit 0; registry load error empty and validation errors empty. |
| `git diff --check` | PASS | Exit 0. |
| `git diff --cached --check` | PASS | Exit 0 with nothing staged at validation time. |

## Focused RepoX Result

Focused tuple `inv_repox_rules` remains failing by design for this partial remediation. Contract registry failures are eliminated, but remaining non-contract RepoX families still block POST-CONVERGE-11.

## Post-Commit Commit Policy Note

The first POST-CONVERGE-10K commit, `2f11713db05e6c9e2afcbc6aac9ba5532b349f8d`, failed the post-commit AIDE commit check because the `## Changelog` bullets used lower-case category prefixes. The task forbids amend/squash, so this follow-up evidence update records the policy issue without rewriting history.
