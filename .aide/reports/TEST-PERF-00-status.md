Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# TEST-PERF-00 Status

Result: PASS_WITH_WARNINGS

TEST-PERF-00 added a tiered validation policy and tooling path for fast validation decisions.

## Completed

- Canonical `verify` CTest discovery was repaired locally by running `cmake --preset verify`.
- `dom_add_testx` now attaches CTest labels directly.
- `ctest --preset verify -N` discovers 493 tests after configure.
- `ctest --preset verify -N -L smoke` discovers 57 smoke tests after label repair and reconfigure.
- `tests/validation_tiers.json` defines fast, focused, component, timing, and full-promotion tiers.
- `scripts/test_tier.py`, `scripts/test_impacted.py`, and `scripts/test_timing_report.py` provide deterministic stdlib-only local validation helpers.
- AIDE Lite text writing compatibility was repaired so `aide_lite.py test` passes inside T0.

## Not Done

- Full CTest was not run.
- Product boot proof was not run.
- Package, release, and portable projection proof were not run.
- RepoX semantic failures from POST-CONVERGE-10K were not remediated.

## Next

Use `python scripts/test_impacted.py --from HEAD~1` to choose normal post-change validation. Continue with `POST-CONVERGE-10L` for remaining RepoX semantics, or run `TEST-PERF-01` for full-suite sharding and slow-test baseline work.
