# NAME-00 Validation

Status: `PASS`

Redo snapshot: 2026-05-18 at `148a9adf95bb678da16784434221c568f7bb96cb`.

## Commands Run

| Command | Result |
| --- | --- |
| `git status --short --branch` | pass; clean at start |
| `git remote -v` | pass |
| `git fetch --all --prune` | pass |
| `git rev-parse HEAD` | pass; `148a9adf95bb678da16784434221c568f7bb96cb` |
| `git rev-parse origin/main` | pass; `148a9adf95bb678da16784434221c568f7bb96cb` |
| `git log --oneline --decorate --graph --max-count=30 --all` | pass |
| `git merge-base --is-ancestor origin/main HEAD` | pass |
| `git merge-base --is-ancestor HEAD origin/main` | pass |
| `py -3 .aide/scripts/aide_lite.py doctor` | pass |
| `py -3 .aide/scripts/aide_lite.py validate` | pass with existing warning: missing `.aide/verification/review-decision-policy.yaml` review ref |
| `py -3 .aide/scripts/aide_lite.py test` | pass |
| `py -3 .aide/scripts/aide_lite.py selftest` | pass |
| `py -3 .aide/scripts/aide_lite.py tools validate` | pass |
| `py -3 .aide/scripts/aide_lite.py roots validate` | pass |
| `py -3 .aide/scripts/aide_lite.py repo validate` | pass |
| `py -3 -m py_compile tools/validators/repo/check_no_src_source_dirs.py tools/validators/repo/check_path_terms.py tools/validators/repo/check_directory_naming.py tools/validators/repo/check_file_naming.py` | pass |
| JSON parse for `contracts/repo/naming.schema.json` and `.aide/reports/NAME-00-*.json` | pass |
| `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .` | pass with warnings |
| `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --json` | pass; 106 findings, 13 warnings, 0 blockers |
| `python tools/validators/repo/check_path_terms.py --repo-root .` | pass with warnings |
| `python tools/validators/repo/check_path_terms.py --repo-root . --json` | pass; 1,450 findings, 78 warnings, 0 blockers |
| `python tools/validators/repo/check_directory_naming.py --repo-root .` | pass with warnings |
| `python tools/validators/repo/check_directory_naming.py --repo-root . --json` | pass; 418 findings, 39 warnings, 0 blockers |
| `python tools/validators/repo/check_file_naming.py --repo-root .` | pass with warnings |
| `python tools/validators/repo/check_file_naming.py --repo-root . --json` | pass; 5,361 findings, 4,307 warnings, 0 blockers |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass |
| `git diff --check` | pass |

## Not Run

- Full CTest was not run because NAME-00 is a naming-law task and full CTest remains governed by TEST-PERF-01 sharding.
- Focused RepoX and smoke CTest were not rerun by this redo because no test/CMake/product behavior changed.
- CMake configure/build was not rerun because no product/runtime/build behavior changed.
- Package, projection, release, full eval, GitHub release, tag, upload, and settings operations were not run.

## Notes

The new naming validators intentionally classify existing debt. They do not weaken the existing strict layout/root/distribution/component validators, which still pass.
