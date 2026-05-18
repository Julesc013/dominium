Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# SEMANTIC-LINTS Validation

Result: PASS_WITH_WARNINGS.

## Sync And Setup

- `git status --short --branch`: clean at task start.
- `git fetch --all --prune`: PASS.
- `git rev-parse HEAD`: `0ffada2872215a527c998afeadf1c18e101a30a4`.
- `git rev-parse origin/main`: `0ffada2872215a527c998afeadf1c18e101a30a4`.
- Merge-base ancestor checks: PASS both ways before edits.

## Focused Semantic Lints

- `ctest --preset verify -R slice0_hardcoded_ids --output-on-failure --timeout 300`: FAIL before repair, PASS after repair in 7.93 seconds.
- `ctest --preset verify -R slice1_hardcoded_constants --output-on-failure --timeout 300`: FAIL before repair, PASS after repair in 3.00 seconds.
- `ctest --preset verify -R "slice0_hardcoded_ids|slice1_hardcoded_constants" --output-on-failure --timeout 300`: PASS in 11.01 seconds after repair; final rerun PASS in 11.06 seconds after line-ending normalization.
- `py -3 -m py_compile tests/app/semantic_lint_common.py tests/app/slice0_hardcoded_ids.py tests/app/slice1_hardcoded_constants.py`: PASS.

## AIDE

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: PASS.

## Strict Validators

- `python tools/validators/check_repo_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`: PASS.
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`: PASS.
- `python tools/validators/check_component_matrices.py --repo-root . --strict`: PASS.

The repo-layout validator refreshed generated migration inventory timestamps during execution. That generated timestamp/hash churn was restored and not staged.

## NAME-00 Validators

- `python tools/validators/repo/check_no_src_source_dirs.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_path_terms.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_directory_naming.py --repo-root .`: PASS_WITH_WARNINGS.
- `python tools/validators/repo/check_file_naming.py --repo-root .`: PASS_WITH_WARNINGS.

Warnings remain the NAME-00 classified transitional naming debt.

## Supplemental

- `python scripts/verify_docs_sanity.py --repo-root .`: PASS.
- `python scripts/verify_build_target_boundaries.py --repo-root .`: PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .`: PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .`: PASS.
- JSON parse for semantic findings, disposition, readiness, allowlist, and allowlist schema: PASS.
- Allowlist consistency check: PASS; 1,104 entries, no duplicate exact keys.

## CTest Gates

- `ctest --preset verify -R inv_repox_rules --output-on-failure --timeout 300`: PASS in 118.55 seconds after correcting the new disposition doc status from `CANONICAL` to `DERIVED`.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS, 57/57 tests, 51.25 seconds.

Full monolithic CTest was not run in this task. TEST-PERF-01 defines the full/sharded execution model, and this task was scoped to the two semantic lint blockers plus focused post-repair validation.

## Build/Release

- CMake configure/build was not rerun. No CTest registration, build target, product/runtime/game, package, profile, bundle, or release behavior changed.
- Release/package/projection generation was not run.

## Notes

- A first focused RepoX rerun failed because `docs/testing/SEMANTIC_LINT_DISPOSITION.md` was initially marked `CANONICAL`. The file is a derived disposition guide, so the status was corrected to `DERIVED`; no canon-index or identity-fingerprint churn was kept.
- No broad suppressions were added.
- No tests were deleted.
- No assertions were removed.
