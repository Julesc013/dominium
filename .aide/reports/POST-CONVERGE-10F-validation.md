# POST-CONVERGE-10F Validation

## Focused CTest

| Command | Result | Notes |
| --- | --- | --- |
| `ctest --preset verify -N` | pass, 0 tests | canonical preset discovery gap |
| `ctest --preset verify -R invariant_units_present --output-on-failure` | pass, no tests found | canonical preset discovery gap |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | pass, no tests found | canonical preset discovery gap |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -N` | pass, 493 tests | tuple build has discoverable tests |
| `python tests/contract/unit_annotation_validation.py --repo-root .` | pass | `Unit annotation validation OK. units=59` |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R invariant_units_present --output-on-failure` | pass | 1/1 passed |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | fail | broad RepoX drift remains |

## AIDE

| Command | Result |
| --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | pass |
| `py -3 .aide/scripts/aide_lite.py validate` | pass |
| `py -3 .aide/scripts/aide_lite.py test` | pass |
| `py -3 .aide/scripts/aide_lite.py selftest` | pass |
| `py -3 .aide/scripts/aide_lite.py tools validate` | pass |
| `py -3 .aide/scripts/aide_lite.py roots validate` | pass |
| `py -3 .aide/scripts/aide_lite.py repo validate` | pass |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | pass |

## Validators

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | known exceptions applied |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | known exceptions applied |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | no warnings |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | no warnings |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | boundary OK |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary OK |
| `python -m json.tool data/registries/unit_registry.json` | pass | JSON parses |

## Git

| Command | Result |
| --- | --- |
| `git status --short --branch` | scoped changes only |
| `git diff --check` | pass |
| `git diff --cached --check` | pass after staging |

## Not Run

Full CTest was not rerun because focused `inv_repox_rules` still fails. Build/package/release generation and product binaries were not run.
