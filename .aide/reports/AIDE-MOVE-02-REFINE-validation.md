# AIDE-MOVE-02-REFINE Validation

## Summary

Validation passed or passed with known non-blocking warnings. No move, delete, rename, reference rewrite, salvage-map application, move-map application, alias, shim, or exception retirement occurred.

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | Passed after latest task/review packet sections were completed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Passed after latest task/review packet sections were completed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest committed AIDE-MOVE-02-PLAN commit passed. |

## JSON Parsing

| Command | Result | Notes |
| --- | --- | --- |
| Parse `.aide/reports/AIDE-MOVE-02-REFINE-candidates.json` | PASS | JSON parsed. |
| Parse `.aide/refactors/AIDE-MOVE-02.no_candidate.json` | PASS | JSON parsed. |

## Existing Validators

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Passed with existing root exceptions and Python `tomllib` fallback warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Passed with existing root exceptions and Python `tomllib` fallback warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | Passed. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | Passed. |

The strict layout/root validators rewrote timestamp/SHA headers in generated migration metadata as a side effect. Those changes were reverted because AIDE-MOVE-02-REFINE is not allowed to write `tools/migration/**`.

## Supplemental

| Command | Result | Notes |
| --- | --- | --- |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Passed. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | Passed. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | Passed. |

## Git

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Only scoped AIDE/refinement and root-recycling docs changes are present. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors at validation time. |

## Not Run

- Full eval.
- Full CTest.
- CMake configure/build.
- Build/package/release generation.
- Product binaries.
- Unknown XStack/AuditX/RepoX/TestX execution.
