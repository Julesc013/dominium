# AIDE-MOVE-02-PLAN Validation

## Summary

Validation passed or passed with known non-blocking warnings. No move, delete, rename, reference rewrite, salvage-map application, move-map application, alias, shim, or exception retirement occurred.

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE lightweight tests passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE selftest passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | AIDE tool validation passed. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | AIDE root validation passed. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | AIDE repo validation passed. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest committed task passed commit policy. |

## Plan Parsing

| Command | Result | Notes |
| --- | --- | --- |
| Parse AIDE-MOVE-02 JSON plans with `py -3` | PASS | Plan, reference rewrite, validation, rollback, exception, and summary JSON parsed. |
| Parse `.aide/refactors/AIDE-MOVE-02.plan.toml` with `tomllib` | PASS | TOML parsed with `py -3`. |

## Existing Validators

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Passed with existing root exceptions and Python `tomllib` fallback warning. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Passed with existing root exceptions and Python `tomllib` fallback warning. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | Passed. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | Passed. |

The strict layout/root validators rewrote timestamp/SHA headers in generated migration metadata as a side effect. Those changes were reverted because AIDE-MOVE-02-PLAN is not allowed to write `tools/migration/**`.

## Supplemental

| Command | Result | Notes |
| --- | --- | --- |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity passed. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | Build boundary check passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity passed. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check passed. |

## Git

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Branch is `main`; local matched `origin/main` before edits. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |

## Not Run

- Full eval.
- Full CTest.
- CMake configure/build.
- Build/package/release generation.
- Product binaries.
- Unknown XStack/AuditX/RepoX/TestX execution.
