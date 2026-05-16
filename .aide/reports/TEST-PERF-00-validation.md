Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# TEST-PERF-00 Validation

This report records validation for tiered test selection and CTest discovery work.

## Commands Run Before Final Validation

| Command | Result | Notes |
| --- | --- | --- |
| `git fetch --all --prune` | pass | local and origin aligned |
| `ctest --preset verify -N` | pass, 0 tests before configure | baseline discovery issue |
| `cmake --preset verify` | pass | configure-only refresh |
| `ctest --preset verify -N` | pass, 493 tests after configure | canonical discovery repaired locally |
| `ctest --preset verify -N -L smoke` | pass, 57 tests after label repair and reconfigure | smoke label selection works |
| `python -m json.tool tests/validation_tiers.json` | pass | manifest parses |
| `python -m py_compile scripts/test_tier.py scripts/test_impacted.py scripts/test_timing_report.py` | pass | helper scripts compile |
| `python scripts/test_tier.py --list` | pass | tiers list correctly |
| `python scripts/test_tier.py --tier ctest-smoke --dry-run` | pass | commands render without running smoke tests |
| `python scripts/test_impacted.py --from HEAD~1 --include-worktree --dry-run` | pass | impacted tier selection works |
| `python scripts/test_tier.py --tier t0` | fail, then pass after fixes | exposed AIDE packet-template and writer compatibility issues; final run passed |
| `python scripts/test_tier.py --tier timing-sample` | pass | `invariant_units_present` timing sample passed in 1.078s |

## Final Validation

| Command | Result |
| --- | --- |
| `python scripts/test_tier.py --tier t0` | PASS |
| `python scripts/test_tier.py --tier timing-sample` | PASS |
| `ctest --preset verify -N` | PASS, 493 tests discovered |
| `ctest --preset verify -N -L smoke` | PASS, 57 tests discovered |
| `py -3 .aide/scripts/aide_lite.py tools validate` | PASS |
| `py -3 .aide/scripts/aide_lite.py roots validate` | PASS, generated tracked migration-map refresh was reverted as out of scope |
| `py -3 .aide/scripts/aide_lite.py repo validate` | PASS |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS with known TOML fallback warnings |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS with known TOML fallback warnings |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS with known TOML fallback warning |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS with known TOML fallback warning |
| `python scripts/test_impacted.py --from HEAD~1 --include-worktree --dry-run --json-out .dominium.local/test-perf-00/impacted-dry-run.json` | PASS |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS after final report/doc edits |
| `python -m json.tool tests/validation_tiers.json` and TEST-PERF JSON reports | PASS after final report/doc edits |
| `python -m py_compile scripts/test_tier.py scripts/test_impacted.py scripts/test_timing_report.py` | PASS after final report/doc edits |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS, no staged diff |
| `py -3 .aide/scripts/aide_lite.py commit check --latest` | PASS for pre-existing latest commit |

Full CTest, product boot proof, package proof, release proof, and portable projection proof were not run.
