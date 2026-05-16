# AIDE-GATE-03 Validation

## Commands

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Clean before gate evidence. |
| `git remote -v` | PASS | origin remote present. |
| `git fetch --all --prune` | PASS | Remote remained equal to local HEAD. |
| `git rev-parse HEAD` | PASS | `9a05800601809463ea596a84e2c8bdc9fcffdbad`. |
| `git rev-parse origin/main` | PASS | `9a05800601809463ea596a84e2c8bdc9fcffdbad`. |
| `git log -1 --oneline` | PASS | `9a0580060 chore(repo): move IDE projection notes into docs`. |
| `git merge-base --is-ancestor origin/main HEAD` | PASS | Exit code 0. |
| `git merge-base --is-ancestor HEAD origin/main` | PASS | Exit code 0. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | AIDE commit check passed for AIDE-MOVE-01-APPLY. |
| `py -3 .aide/scripts/aide_lite.py commit check --message-file .git/AIDE_GATE_03_COMMIT_MSG.txt` | PASS | AIDE-GATE-03 commit message passed before commit. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; non-blocking `tomllib` fallback warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; non-blocking `tomllib` fallback warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; non-blocking `tomllib` fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; non-blocking `tomllib` fallback warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity passed. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity passed. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check passed. |
| `rg -l "ide/README\\.md|/ide/README\\.md" .` | PASS_WITH_WARNINGS | Remaining matches are generated review, historical audit, or root-recycling evidence. |
| `rg -l "docs/architecture/IDE_PROJECTIONS\\.md|/docs/architecture/IDE_PROJECTIONS\\.md" .` | PASS | New path appears in expected docs/tool references. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged changes at validation time. |

## Not Run

- Full eval: out of scope.
- Full CTest: out of scope.
- CMake configure/build: out of scope.
- Package/release generation: out of scope.
- Product binaries: out of scope.
