# POST-CONVERGE-11 Validation

Status: DERIVED
Last Reviewed: 2026-05-17

## Initial Sync

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | PASS | Worktree started clean; branch `main` ahead of `origin/main` by expected POST-CONVERGE commits. |
| `git remote -v` | PASS | `origin` points to `https://github.com/Julesc013/dominium.git`. |
| `git fetch --all --prune` | PASS | Remote refs fetched. |
| `git rev-parse HEAD` | PASS | `933a17ce80044a3dceb38f6c737ad22f73a7b643`. |
| `git rev-parse origin/main` | PASS | `fab604957d04af223a24a353c0bd3c509668010d`. |
| `git log -1 --oneline` | PASS | `933a17ce8 audit(repo): classify RepoX closeout blockers`. |
| `git merge-base --is-ancestor origin/main HEAD` | PASS | `origin/main` is ancestor of local HEAD. |
| `git merge-base --is-ancestor HEAD origin/main` | PASS_WITH_NOTES | Local HEAD is ahead of `origin/main`. |

## RepoX Readiness Gate

| Command | Result | Notes |
| --- | --- | --- |
| `ctest --preset verify -N` | PASS_WITH_NOTES | Canonical verify discovery reports 493 tests; missing-executable notices remain because POST-CONVERGE-11 did not build. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | FAIL_EXPECTED | 20 failures / 5 warnings. RepoX remains a semantic blocker. |

## Product Boot Commands

No product boot commands were run. The task requires POST-CONVERGE-11 to stop before product binary execution when focused RepoX is still a semantic blocker.

## AIDE

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | No hard validation failures detected. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | Latest task/review packets pass policy checks. |
| `py -3 .aide/scripts/aide_lite.py test` | PASS | Internal AIDE checks pass. |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS | Internal AIDE selftest checks pass. |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS | Tool inventory/wrap-plan validation passes. |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS | Root validation passes; generated timestamp/head churn in `tools/migration/*` was not kept. |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS | Repo intelligence validation passes. |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS | Latest pre-11 commit policy check passes. |

## Existing Validators

| Command | Result |
| --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS |

## Supplemental

| Command | Result |
| --- | --- |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS |

## Data And Git

| Command | Result | Notes |
| --- | --- | --- |
| `python -m json.tool .aide/reports/POST-CONVERGE-11-product-boot-results.json` | PASS | JSON parses. |
| `python -m json.tool .aide/reports/POST-CONVERGE-11-next-readiness.json` | PASS | JSON parses. |
| JSONL parse for `.aide/ledgers/migration_ledger.jsonl` | PASS | 32 non-empty lines parse. |
| `git status --short --branch` | PASS | Shows only scoped POST-CONVERGE-11 evidence/status changes before staging. |
| `git diff --check` | PASS | No whitespace errors before staging. |
| `git diff --cached --check` | PASS | No staged whitespace errors. |

## Not Run

- Build: not run because product boot proof is blocked by RepoX readiness.
- Full CTest: not run because focused RepoX still has hard semantic failures.
- Product boot proof: not run because focused RepoX is a semantic blocker.
- Portable projection proof, package proof, and release proof: not run by scope.
