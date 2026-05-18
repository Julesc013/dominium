# NAME-00 Validation

Status: `PASS`

## Commands Run

| Command | Result |
| --- | --- |
| `git status --short --branch` | pass; clean at start |
| `git remote -v` | pass |
| `git fetch --all --prune` | pass |
| `git rev-parse HEAD` | pass; `9e383abd45250b8ae020f0f2f96476212bfa3160` |
| `git rev-parse origin/main` | pass; `9e383abd45250b8ae020f0f2f96476212bfa3160` |
| `git log --oneline --decorate --graph --max-count=30 --all` | pass |
| `git merge-base --is-ancestor origin/main HEAD` | pass |
| `git merge-base --is-ancestor HEAD origin/main` | pass |
| `py -3 .aide/scripts/aide_lite.py doctor` | pass |
| `py -3 .aide/scripts/aide_lite.py validate` | pass |
| `py -3 .aide/scripts/aide_lite.py pack --task "NAME-00 Directory File Language and Ownership Naming Canon"` | pass |
| `py -3 -m py_compile tools/validators/repo/check_no_src_source_dirs.py tools/validators/repo/check_path_terms.py tools/validators/repo/check_directory_naming.py tools/validators/repo/check_file_naming.py` | pass |
| JSON parse for `contracts/repo/naming.schema.json` and `.aide/reports/NAME-00-*.json` | pass |
| TOML parse for `contracts/repo/naming.contract.toml` | pass |
| `py -3 tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict --json` | pass; 0 blockers, 13 warnings |
| `py -3 tools/validators/repo/check_path_terms.py --repo-root . --strict --json` | pass; 0 blockers, 78 warnings |
| `py -3 tools/validators/repo/check_directory_naming.py --repo-root . --json` | pass; warning-only classifier |
| `py -3 tools/validators/repo/check_file_naming.py --repo-root . --json` | pass; warning-only classifier |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass |
| `ctest --preset verify -C Debug -R ^inv_repox_rules$ --output-on-failure` | pass; 1/1 |
| `ctest --preset verify -C Debug -L smoke --timeout 300 --output-on-failure` | pass; 57/57 |
| `git diff --check` | pass |

## Not Run

- Full CTest was not run because NAME-00 is a naming-law task and full CTest remains governed by the next semantic lint repair/proof sequence.
- CMake configure/build was not rerun because no product/runtime/build behavior changed.
- Package, projection, release, full eval, GitHub release, tag, upload, and settings operations were not run.

## Notes

The new naming validators intentionally classify existing debt. They do not weaken the existing strict layout/root/distribution/component validators, which still pass.
