Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-01

# MOVE-ROUTER-01 Validation

## Structural Apply

| Check | Result | Notes |
| --- | --- | --- |
| MOVE-ROUTER-00 prerequisites | PASS | Naming contract, bad-root routing contract, schema, router, and route table existed and parsed. |
| Router py_compile | PASS | `python -m py_compile tools/migration/route_bad_roots.py`. |
| Pre-apply dry-run | PASS | 1,765 bad-root tracked files; 1,694 semantic routes; 71 quarantine routes; 0 collisions; 0 impossible routes. |
| Apply pass | PASS | 1,765 tracked files moved with `git mv`; 0 skipped. |
| Bad-root tracked file count | PASS | 24 former bad roots now have 0 tracked files. |
| Exception ledger | PASS | 23 active bad-root exceptions retired under `retired_exceptions`; `ide_root` was already retired. |
| Empty root shell cleanup | PASS | Removed only untracked `__pycache__/*.pyc` leftovers and empty former-root directories after tracked-file moves. No tracked file was deleted. |

## AIDE

| Command | Result |
| --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS_WITH_WARNINGS |
| `py -3 .aide/scripts/aide_lite.py test` | PASS |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS |

`aide validate` retained the pre-existing review-packet reference warning, but exited successfully.

## Validators

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS | Active exceptions now cover only remaining non-router exceptions. |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS | No unexcepted transitional bad roots remain. |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS | Distribution logical roots/projections intact. |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS | Component matrix sections/statuses/tier evidence intact. |
| `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .` | PASS_WITH_WARNINGS | 93 archive/historical info findings; 0 warnings. |
| `python tools/validators/repo/check_forbidden_root_names.py --repo-root .` | PASS_WITH_WARNINGS | Existing advisory findings remain warning-only for later naming cleanup. |
| `python tools/validators/repo/check_bad_root_absence.py --repo-root . --json` | PASS | `tracked_bad_root_file_count = 0`. |

## Supplemental Checks

| Command | Result |
| --- | --- |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS |
| `git diff --check` | PASS |
| `git diff --cached --check` | WARN | Pre-existing trailing whitespace surfaced in moved `docs/development/templates/adapter_template.md`; content was left untouched by MOVE-ROUTER-01. |

## Not Run

- Full CTest: out of scope for MOVE-ROUTER-01.
- CMake configure/build: deferred to MOVE-ROUTER-02/proof because this task intentionally does not repair references or build paths.
- Product boot, projection generation, release generation: out of scope and intentionally not run.

## Known Warnings

- Stale references/imports/build paths remain after the physical move and are assigned to `MOVE-ROUTER-02`.
- Quarantined files are inactive pending owner review.
- New naming validators remain advisory where they report historical archive terms or transitional cleanup warnings.
- The staged whitespace warning in the moved adapter template is intentionally
  left for a later cleanup task because MOVE-ROUTER-01 does not edit moved file
  contents.
