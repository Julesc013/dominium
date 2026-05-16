# AIDE-MOVE-01-APPLY Validation

## Commands

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Clean before apply; later showed only scoped move/reference/report changes. |
| `git remote -v` | PASS | origin points to `https://github.com/Julesc013/dominium.git`. |
| `git rev-parse HEAD` | PASS | `8e03222fa4ed11ea3cf95429f361507745ea7bb0`. |
| `git rev-parse origin/main` | WARN | Observed `8e03222fa4ed11ea3cf95429f361507745ea7bb0`; prompt expected older `ab7362987bcff405cac69d947efb1950cb2f2295`. |
| `git log -1 --oneline` | PASS | `8e03222fa chore(aide): approve first low-risk move plan`. |
| Plan and gate JSON inspection | PASS | Gate authorizes only AIDE-MOVE-01-APPLY for `ide/README.md -> docs/architecture/IDE_PROJECTIONS.md`. |
| `git ls-files ide/README.md` | PASS | Source was tracked before apply. |
| `git ls-files docs/architecture/IDE_PROJECTIONS.md` | PASS | Target was not tracked before apply. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest committed message passed before this apply commit. |
| `py -3 .aide/scripts/aide_lite.py commit check --message-file .git/AIDE_MOVE_01_APPLY_COMMIT_MSG.txt` | PASS | Apply commit message passed before commit. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; Python emitted non-blocking `tomllib` fallback warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; Python emitted non-blocking `tomllib` fallback warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; Python emitted non-blocking `tomllib` fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; Python emitted non-blocking `tomllib` fallback warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity passed. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity passed. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check passed. |
| `python -m py_compile scripts/verify_docs_sanity.py tools/aide/select_move_wave.py` | PASS | Modified Python files compile. |
| `rg -l "ide/README\\.md|/ide/README\\.md" .` | PASS_WITH_WARNINGS | Remaining matches are historical/root-recycling planning docs, generated architecture registry/graph review items, and historical audit evidence. |
| `git diff --check` | PASS | No whitespace errors before staging. |

## Not Run

- Full eval: out of scope.
- Full CTest: out of scope.
- CMake configure/build: out of scope.
- Package/release generation: out of scope.
- Product binaries: out of scope.
