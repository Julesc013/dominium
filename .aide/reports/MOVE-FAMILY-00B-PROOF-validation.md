Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00B-PROOF Validation

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Initial state clean on `main...origin/main`. |
| `git remote -v` | PASS | origin is `https://github.com/Julesc013/dominium.git`. |
| `git fetch --all --prune` | PASS | origin/main remained equal to HEAD. |
| `git rev-parse HEAD` | PASS | `7077e317c3c87a75036c8b76fe70cce112ef0bbc`. |
| `git rev-parse origin/main` | PASS | `7077e317c3c87a75036c8b76fe70cce112ef0bbc`. |
| `git merge-base --is-ancestor origin/main HEAD` | PASS | true. |
| `git merge-base --is-ancestor HEAD origin/main` | PASS | true. |
| `git merge-base --is-ancestor 7077e317c3c87a75036c8b76fe70cce112ef0bbc HEAD` | PASS | expected apply commit present. |
| `git ls-files ide` | PASS | empty. |
| filesystem `ide` listing | PASS | `ide_path_exists=false`. |
| `git status --short ide` | PASS | no dirty state. |
| `git ls-files contracts/projections/ide` | PASS | all three moved manifest files are tracked. |
| manifest JSON parse and required-field check | PASS | schema and both examples parse; examples include all schema-required fields. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest commit message passed policy. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Passed with known TOML fallback-parser warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Passed with known TOML fallback-parser warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Passed with known TOML fallback-parser warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Passed with known TOML fallback-parser warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | PASS | 1/1 test passed in 143.69 seconds. |
| targeted old source path scan | PASS | No active script/tool/CMake/test/current-architecture reference to retired schema/example source paths. |
| generated/local ignored check | PASS_WITH_WARNINGS | `.aide.local/` and `.dominium.local/` remain ignored; no tracked files under those roots. |

## Not Run

- Full CTest: not run by proof scope.
- Full eval: not run by proof scope.
- CMake configure/build: not run by proof scope.
- Product binaries: not run by proof scope.
- Package/release generation: not run by proof scope.
- Portable projection regeneration: not run by proof scope.
- Internal pilot release regeneration: not run by proof scope.
