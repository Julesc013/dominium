Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C-A-PLAN Validation

## Actual Validation Results

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Branch `main`; only scoped planning/evidence/doc changes plus ignored local output. |
| `git fetch --all --prune` | PASS | `origin/main` equals local task baseline at start. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS_WITH_WARNINGS | Warnings: compact task packet over target and existing review-packet referenced path warning. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | AIDE Lite internal test suite passed. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | AIDE Lite internal selftest suite passed. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool recycling evidence validates; no unknown tool execution. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root recycling evidence validates; no moves/deletes/reference rewrites. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo intelligence evidence validates. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest pre-task commit message passes policy. |
| MOVE-FAMILY-00C-A JSON parse | PASS | 11 new 00C-A JSON planning/report artifacts parse. |
| MOVE-FAMILY-00C-A TOML parse | PASS_WITH_WARNINGS | Python environment lacks `tomllib`; manual fallback key inspection verified required plan keys. |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; known fallback TOML parser warnings. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; known fallback TOML parser warnings. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; known fallback TOML parser warning. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS_WITH_WARNINGS | Strict result passed; known fallback TOML parser warning. |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS | Docs sanity OK. |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS | `BOUNDARY-OK`: build boundary checks passed. |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS | UI shell purity OK. |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS | ABI boundary check OK. |
| Strict validator metadata side effect check | PASS_WITH_WARNINGS | Validators refreshed `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json`; timestamp/head churn was restored because those files are outside this planning task's write scope. |
| `git diff --check` | PASS | No whitespace errors. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |
| Generated output ignored check | PASS | `.aide.local/` and `.dominium.local/` are ignored and not tracked. |

## Not Run By Scope

- Full CTest.
- Full eval.
- CMake configure/build.
- Package/release generation.
- Product binaries.
- Move/apply commands.
- Unknown XStack/AuditX/RepoX/TestX execution.

## Post-Commit Policy Note

- The first task commit used the prompt-specified subject `aide(move): plan validation shim migration`.
- Local AIDE commit policy rejected `aide` as a commit type during post-commit `commit check --latest`.
- The task forbids amend/rebase/reset, so the policy mismatch is recorded by a follow-up `audit(...)` evidence commit rather than rewriting history.
