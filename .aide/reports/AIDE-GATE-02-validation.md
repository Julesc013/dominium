# AIDE-GATE-02 Validation

## Status

Final validation result: PASS.

## Results

| Command | Result | Notes |
| --- | --- | --- |
| Plan JSON/TOML inspection | PASS | All AIDE-MOVE-01 plan files parsed; no-apply invariants remain false. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE focused tests passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tools validate passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE roots validate passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validate passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest commit check passed. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict repo layout passed; this Python emitted a non-blocking `tomllib` fallback warning. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict root allowlist passed; this Python emitted a non-blocking `tomllib` fallback warning. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Distribution layout passed; this Python emitted a non-blocking `tomllib` fallback warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Component matrices passed; this Python emitted a non-blocking `tomllib` fallback warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity passed. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity passed. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check passed. |
| `git status --short --branch` | PASS | Expected local-ahead gate evidence state. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |

## Not Run

- Full eval: out of scope.
- Full CTest: out of scope.
- CMake configure/build: forbidden by gate scope.
- Package/release generation: forbidden by gate scope.
- Product binaries: forbidden by gate scope.
- Move/apply commands: forbidden by gate scope.
