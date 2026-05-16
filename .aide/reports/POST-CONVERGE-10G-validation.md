# POST-CONVERGE-10G Validation

Status: PARTIAL

## Focused Validation Run So Far

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | pass | Initial state clean; final state dirty only from scoped 10G edits before commit. |
| `git fetch --all --prune` | pass | origin/main matched local HEAD at task start. |
| `git merge-base ancestry checks` | pass | HEAD and origin/main were equal at ae0ded5997b8c496ea992166913e8857ca9a8372. |
| `ctest --preset verify -N` | pass_with_warning | Canonical verify preset discovers 0 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | pass_with_warning | No matching tests in canonical verify discovery; exit 0 with no tests found. |
| `python scripts/ci/check_repox_rules.py --repo-root . --proof-manifest-out .dominium.local/ctest/repox/proof_manifest.json --profile-out .dominium.local/ctest/repox/REPOX_PROFILE.json` | fail_expected | RepoX reduced from 1844 failures to 1769; warnings remain 5. |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | fail_expected | Focused tuple CTest still fails with 1769 RepoX failures and 5 warnings. |
| `python -m py_compile scripts/ci/check_repox_rules.py` | pass | RepoX rule implementation compiles. |

## RepoX Counts

| Metric | Before | After |
| --- | ---: | ---: |
| Failures | 1844 | 1769 |
| Warnings | 5 | 5 |

## Final Validation Suite

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | pass | Passed after restoring the required AIDE task/review packet sections. |
| `py -3 .aide/scripts/aide_lite.py validate` | pass | Passed after restoring the required AIDE task/review packet sections. |
| `py -3 .aide/scripts/aide_lite.py test` | pass | Internal AIDE tests passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | pass | Internal AIDE selftests passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | pass | AIDE tool inventory/wrapper validation passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | pass | AIDE root validation passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | pass | AIDE repo validation passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | pass | Latest commit passed structured commit check. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | Strict repo layout validator passed. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | Strict root allowlist validator passed. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass_with_warning | Strict distribution layout validator passed; Python emitted the known `tomllib` fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | Strict component matrix validator passed. |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK. |
| JSON parse for 10G reports | pass | Parsed `POST-CONVERGE-10G-repox-failure-families.json` and `POST-CONVERGE-10G-repox-before-after.json`. |
| `python -m py_compile scripts/ci/check_repox_rules.py` | pass | RepoX rule implementation compiles. |
| `git diff --check` | pass | No whitespace errors. |
| `git diff --cached --check` | pass | No staged whitespace errors at validation time. |

## Generated Side Effects

Strict validators rewrote `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` timestamps/HEAD fields during validation. Those generated side effects are outside this task's write scope and were removed before staging.
