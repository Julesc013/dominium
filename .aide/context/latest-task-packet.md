# AIDE Latest Task Packet

## PHASE

TEST-PERF-00 - CTest Partition and Wall-Time Policy

## GOAL

Make validation faster to choose and conduct by adding tiered validation, impacted test selection, CTest discovery repair evidence, and bounded timing sampling.

## WHY

Full CTest is too expensive as the default feedback loop. Dominium needs a fast evidence ladder: T0 checks, impacted tests, component tiers, timing samples, and full CTest as a promotion gate.

## CURRENT RESULT

PASS_WITH_WARNINGS. Canonical `verify` CTest discovery is restored after `cmake --preset verify`; CTest smoke labels now select 57 tests after reconfigure. Focused RepoX remains blocked from POST-CONVERGE-10K.

## CONTEXT_REFS

- `tests/validation_tiers.json`
- `scripts/test_tier.py`
- `scripts/test_impacted.py`
- `scripts/test_timing_report.py`
- `docs/repo/TEST_VALIDATION_STRATEGY.md`
- `docs/repo/audits/TEST_PERF_00_CTEST_PARTITION_POLICY.md`
- `.aide/reports/TEST-PERF-00-status.md`
- `.aide/reports/TEST-PERF-00-ctest-discovery.json`

## IMPLEMENTATION

TEST-PERF-00 adds a manifest-driven tier runner, changed-path impacted selector, bounded CTest timing sampler, CTest label metadata repair for `dom_add_testx`, and AIDE Lite writer compatibility for the fast tier.

## EVIDENCE

- `cmake --preset verify` repairs local canonical CTest discovery after stale or missing build-tree state.
- `ctest --preset verify -N` reports 493 tests after configure.
- `ctest --preset verify -N -L smoke` reports 57 tests after label repair and reconfigure.
- Helper scripts compile and render expected tier commands.
- `python scripts/test_tier.py --tier t0` passes after the AIDE Lite compatibility fix.

## NON_GOALS

- no product behavior changes
- no test deletion
- no skip-to-green changes
- no RepoX/AuditX/TestX weakening
- no product boot, package, release, or portable projection proof

## ACCEPTANCE

- tier manifest parses as JSON
- helper scripts compile
- impacted selector produces tier choices from changed paths
- canonical CTest discovery and smoke-label discovery are recorded
- full CTest remains a promotion gate

## OUTPUT_SCHEMA

Human-readable reports plus JSON evidence:

- `.aide/reports/TEST-PERF-00-ctest-discovery.json`
- `.aide/reports/TEST-PERF-00-before-after.json`

## TOKEN_ESTIMATE

Latest packet is intended to stay below the AIDE compact-context budget.

## ALLOWED_PATHS

- validation tooling
- CTest test metadata helpers
- AIDE reports/context/ledger
- post-converge and validation docs

## FORBIDDEN_PATHS

- product/runtime/source behavior changes
- test deletion or skip-to-green changes
- RepoX/AuditX/TestX weakening
- product boot proof, package proof, release proof, portable projection proof

## VALIDATION

Manifest JSON parsed; helper scripts compiled; tier listing worked; impacted selection worked; canonical CTest discovery restored to 493 tests after configure; smoke label discovery reports 57 tests.

## NEXT

Recommended semantic task: `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`.

Recommended test-performance follow-up: `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline`.
