# Regression Suites (EXEC-AUDIT1)

This document defines the canonical regression suite used to guard
determinism, performance budgets, and degradation behavior.

Scope: regression tests for determinism, budgets, and degradation.

## Invariants
- Regression suites guard deterministic equivalence across backends.
- Budgets and degradation are enforced deterministically.
- Hash updates require change protocol and audit.

## Dependencies
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/EXECUTION_MODEL.md`

## How to run locally

- Engine regression: `ctest -R execution_perf_regression`
- Shard regression: `ctest -R dominium_server_shard_regression`

Both tests are headless and use fixtures under `game/tests/fixtures/`.

## Fixtures and coverage

- `fixture_earth_only`
  - Minimal world footprint; baseline determinism and budgets.
- `fixture_10k_systems_latent`
  - Latent scaling guard; no global-iteration regressions.
- `fixture_war_campaign`
  - War determinism, budgets, and degradation under pressure.
- `fixture_market_crisis`
  - Economy amortization and budget enforcement under load.
- `fixture_timewarp_1000y`
  - Long-horizon batch invariance.

## What failures mean

- Hash mismatch: determinism regression (step vs batch, EXEC2 vs EXEC3, or sharded).
- Budget breach: performance regression against baseline/modern/server tiers.
- Degradation mismatch: non-deterministic or incorrect degradation behavior.
- Global-iteration guard: latent workloads scaling with total world size.

## Updating expected hashes

Updating `expected_hash` or `expected_degraded_hash` in fixtures requires:
1) Change protocol rationale (ARCH0).
2) Invariant impact analysis.
3) CI matrix update if the enforcement scope changes.

Never update hashes to "fix" a flake.

## Forbidden assumptions
- Hash updates are acceptable without a canon change.
- Degradation differences are benign without investigation.

## See also
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`
