# MOVE-FAMILY-00B-APPLY Validation

## Result

PASS_WITH_WARNINGS.

## Commands

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Started clean on `main...origin/main`. |
| `git remote -v` | PASS | origin is `https://github.com/Julesc013/dominium.git`. |
| `git fetch --all --prune` | PASS | Remote and local remained synchronized. |
| `git rev-parse HEAD` | PASS | Start HEAD: `2cea2a44c7af9e596da3ae79a3246471f010e932`. |
| `git rev-parse origin/main` | PASS | origin/main: `2cea2a44c7af9e596da3ae79a3246471f010e932`. |
| `git merge-base --is-ancestor origin/main HEAD` | PASS | Ancestor check passed. |
| `git merge-base --is-ancestor HEAD origin/main` | PASS | Ancestor check passed. |
| Gate/plan JSON inspection | PASS | MOVE-FAMILY-00B-GATE authorized exactly three moves and five apply rewrite groups. |
| Source/target preflight | PASS | Sources tracked/present; target files absent. |
| `git mv` for three manifests | PASS | Exactly three approved moves applied. |
| `git ls-files ide` | PASS | Empty after apply. |
| Empty `ide/` directory removal | PASS | Only empty directories remained and were removed after path verification. |
| Manifest JSON parse | PASS | Moved schema and two examples parse as JSON. |
| Example structural check | PASS | Both examples contain all schema-required fields. |
| Stale-reference scan | PASS_WITH_WARNINGS | Remaining old-path refs are generated-output, historical/planning, or generated evidence refs. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE test passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest commit check passed before the apply commit. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known TOML fallback warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known TOML fallback warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known TOML fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result pass; known TOML fallback warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | PASS_WITH_WARNINGS | First two runs exposed missing four-line status headers in three touched docs; after metadata repair, rerun passed 1/1. |
| Active stale source-reference scan | PASS | No remaining active script/tool/architecture reference to the old schema/example source paths. |
| `python -m json.tool .aide/reports/MOVE-FAMILY-00B-APPLY-evidence.json` | PASS | Apply evidence JSON parsed. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged diff at check time. |

## Not Run

- Full CTest: not run by scope.
- Full eval: not run by scope.
- CMake configure/build: not run by scope.
- Product binaries: not run by scope.
- Package/release generation: not run by scope.
- Portable projection regeneration/validation: not required by the approved plan.
- Internal pilot release regeneration/validation: not required by the approved plan.
