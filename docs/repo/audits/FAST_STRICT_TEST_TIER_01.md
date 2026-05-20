Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none

# FAST-STRICT-TEST-TIER-01 Audit

## Scope

This task defines the first Foundation Lock proof tier after canonical repo
cleanup. It creates a machine-readable test-tier contract, a fast strict runner,
a contract validator, documentation, and AIDE evidence surfaces.

No feature code, product behavior, renderer behavior, native GUI behavior,
worldgen behavior, or full CTest remediation is in scope.

## Created Surfaces

- `contracts/testing/test_tiers.contract.toml`
- `contracts/testing/test_tiers.schema.json`
- `tools/test/run_fast_strict.py`
- `tools/validators/testing/check_test_tiers.py`
- `docs/testing/test_tier_policy.md`
- `docs/testing/fast_strict_test_tier.md`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-status.md`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-validation.md`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-results.json`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-run.json`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-run.md`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-full-gate-debt.md`
- `.aide/reports/FAST-STRICT-TEST-TIER-01-existing-proof-inventory.md`

## Gate Model

- `fast_strict`: T0 + T1 + T2.
- `extended`: T0 + T1 + T2 + relevant T3.
- `release`: T0 + T1 + T2 + T3 + selected T4.
- `release_candidate`: compatibility alias for `release`.
- `full`: all available T0 + T1 + T2 + T3 + T4.

Full CTest is retained under T4 and is not part of the normal development gate.

## Validation

- `python -m py_compile tools/test/run_fast_strict.py tools/validators/testing/check_test_tiers.py`: PASS.
- `python tools/validators/testing/check_test_tiers.py --repo-root . --strict`: PASS.
- `python tools/validators/testing/check_test_tiers.py --repo-root . --json`: PASS.
- `python tools/test/run_fast_strict.py --repo-root . --list`: PASS.
- `python tools/test/run_fast_strict.py --repo-root . --dry-run`: PASS.
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/FAST-STRICT-TEST-TIER-01-run.json --md-out .aide/reports/FAST-STRICT-TEST-TIER-01-run.md`: PASS, 30/30 commands, 332.828 seconds.

## Full Gate Debt

Full CTest debt is not hidden or reclassified as pass. The follow-up debt task
is `FULL-GATE-DEBT-01`. Historical full CTest evidence recorded by the task
prompt was 440/503 passed, 63 failed, about 3227.41 seconds; this task did not
rerun full CTest.

## Next Task

`PUBLIC-SURFACE-REGISTRY-01`
