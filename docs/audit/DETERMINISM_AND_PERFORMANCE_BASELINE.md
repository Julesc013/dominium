Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Determinism And Performance Baseline

## Scope

Baseline verification for distribution-layer determinism with non-gating performance probes.

## Implemented

- Test added: `tests/distribution/distribution_determinism_performance_tests.py`.
- Determinism checks performed by test:
  - lockfile inspection output equivalence across canonical fixtures:
    - `tests/distribution/fixtures/lockfiles/lockfile_a.json`
    - `tests/distribution/fixtures/lockfiles/lockfile_b.json`
  - capability resolution output digest stability under reversed capability argument ordering.
- Performance probes recorded (non-gating):
  - lockfile inspect runtime (ms)
  - capability dry-run runtime (ms)
  - probe artifact path: `tmp/perf/distribution_baseline.json`.

## Test Integration

- Wired in `tests/distribution/CMakeLists.txt` as `distribution_determinism_performance_baseline`.
- Included under distribution TestX label and executed via standard TestX gate.

## Readiness Statement

- Determinism checks are enforced as pass/fail.
- Performance probe collection is active and non-blocking.
