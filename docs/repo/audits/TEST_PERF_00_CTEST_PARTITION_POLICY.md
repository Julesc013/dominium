Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# TEST-PERF-00 CTest Partition and Wall-Time Policy

## Status

- Task ID: TEST-PERF-00
- Result: PASS_WITH_WARNINGS
- Branch: main
- Scope: validation tooling, CTest discovery, tier policy, and timing evidence
- Product behavior changed: no
- Tests deleted or skipped: no
- RepoX/AuditX/TestX weakened: no

## Prior State

- Full CTest was not a practical default feedback loop.
- Canonical `ctest --preset verify -N` discovered 0 tests before the local verify build tree was refreshed.
- The tuple verify build under `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug` discovered 493 tests and remained the effective focused CTest lane.
- Focused RepoX was still failing from POST-CONVERGE-10K with 51 failures and 5 warnings.

## Changes Made

- Added `tests/validation_tiers.json` as the validation tier and impact-selection manifest.
- Added `scripts/test_tier.py` for named tier execution.
- Added `scripts/test_impacted.py` for changed-path-to-tier selection.
- Added `scripts/test_timing_report.py` for bounded CTest timing samples.
- Repaired `dom_add_testx` label attachment so CTest labels are emitted after configure.
- Repaired AIDE Lite text writing compatibility so `aide_lite.py test` can run in the fast tier.
- Added `docs/repo/TEST_VALIDATION_STRATEGY.md`.

## Discovery Evidence

| Check | Result |
| --- | --- |
| `ctest --preset verify -N` before configure refresh | 0 tests |
| `cmake --preset verify` | pass |
| `ctest --preset verify -N` after configure refresh | 493 tests |
| `ctest --preset verify -N -L smoke` after label repair and reconfigure | 57 tests |

## Tier Model

| Tier | Role |
| --- | --- |
| `t0` | normal fast AIDE and repo sanity gate |
| `ctest-smoke` | configured canonical CTest smoke subset |
| `focused-repox` | focused RepoX blocker reproduction |
| `component-contracts` | contract, schema, invariant, and registry tests |
| `component-distribution` | distribution and release-adjacent tests |
| `component-tools` | tooling and governance tool tests |
| `component-runtime` | runtime, integration, determinism, and platform tests |
| `timing-sample` | bounded timing evidence |
| `full-promotion` | complete canonical CTest promotion gate |

## Wall-Time Classification

The full CTest suite remains the promotion gate. Normal tasks should run T0 plus impacted or component tiers. Full CTest wall-time remains a scheduling concern until a later task records a full timing baseline and optional shard policy.

## Remaining Warnings

- Focused RepoX semantic failures remain from POST-CONVERGE-10K.
- Full CTest was not run in this task.
- Timing evidence is intentionally bounded; it does not replace a full slow-test profile.
- Canonical CTest discovery requires `cmake --preset verify` after build-tree cleanup or stale generated state.
- The fast tier found and fixed an AIDE self-test writer compatibility issue before final validation.

## Next

Continue semantic RepoX remediation with `POST-CONVERGE-10L` or run `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline` if the next priority is wall-time reduction rather than RepoX semantics.
