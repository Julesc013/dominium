# MOVE-FAMILY-00B-GATE Validation

## Result

PASS_WITH_WARNINGS.

## Commands Run

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Initial worktree clean on `main...origin/main`. |
| `git remote -v` | PASS | origin points at `https://github.com/Julesc013/dominium.git`. |
| `git fetch --all --prune` | PASS | Fetched without divergence. |
| `git rev-parse HEAD` | PASS | `32dc93947661c98935d1308f7144eab5e78984bf`. |
| `git rev-parse origin/main` | PASS | `32dc93947661c98935d1308f7144eab5e78984bf`. |
| `git log -3 --oneline` | PASS | Latest commit is `32dc93947 audit(move): plan IDE manifest projection ownership`. |
| `git merge-base --is-ancestor origin/main HEAD` | PASS | Ancestor check passed. |
| `git merge-base --is-ancestor HEAD origin/main` | PASS | Ancestor check passed. |
| `git status --short --ignored .dominium.local .aide.local` | PASS | `.aide.local/` and `.dominium.local/` are ignored local outputs. |
| `git ls-files .dominium.local .aide.local` | PASS | No generated local output is tracked. |
| Plan artifact JSON/TOML parsing and invariant inspection | PASS | Eight plan JSON files and plan TOML parsed; exact three moves; apply disabled. |
| `git ls-files ide` | PASS | Exactly three tracked IDE manifest files. |
| `git ls-files ide/manifests` | PASS | Matches the expected three tracked source files. |
| `git ls-files contracts/projections/ide` | PASS | No tracked target collision. |
| `git status --short ide contracts/projections` | PASS | No dirty source or target paths. |
| Target file existence checks | PASS | Planned target files absent; apply plan creates target path. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest commit message passed. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known minimal TOML fallback warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known minimal TOML fallback warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known minimal TOML fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known minimal TOML fallback warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |

## Not Run

- Full eval: not run by gate scope.
- Full CTest: not run by gate scope.
- CMake configure/build: not run by gate scope.
- Package/release generation: not run by gate scope.
- Product binaries: not run by gate scope.
- Move/apply commands: not run by gate scope.
- Unknown XStack/AuditX/RepoX/TestX execution: not run by gate scope.

## Known Warnings

- `contracts/projections/ide/**` does not exist yet; apply is expected to create it.
- Historical and generated references to `ide/manifests/**` remain warning-only when classified as historical evidence or generated-output paths.
- Strict validators emitted known TOML fallback-parser warnings while passing.

## Final Git Checks

- `python -m json.tool .aide/reports/MOVE-FAMILY-00B-GATE-readiness.json`: PASS.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- Incidental `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json` timestamp/head updates produced by `roots validate` were restored before staging because they are outside this gate's allowed write scope.
