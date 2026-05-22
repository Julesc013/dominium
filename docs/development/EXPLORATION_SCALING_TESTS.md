Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Exploration Scaling Tests

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/archive/audit/CANON_MAP.md` and `docs/archive/audit/DOC_DRIFT_MATRIX.md`.


This guide describes the W1 exploration scaling fixtures and TestX checks.

## Fixtures (data-only)
Fixtures live under:
`tests/performance/exploration_fixtures/`

Each fixture contains a data-only template at:
`tests/fixtures/world/templates/exploration_baseline.worlddef.json`

All fixtures share the same navigation script but differ only in inactive
topology size or depth.

## Tests

- Fixture contracts:
  - `tests/performance/exploration_fixture_contracts.py`
  - Verifies fixture topology size and required fields.

- Scaling integration:
  - `tests/integration/exploration_scaling_tests.py`
  - Runs the same navigation script against all fixtures.
  - Compares derived exploration metrics and replay hashes.
  - Verifies renderer parity across supported backends.

## Running locally

```
cmake --build --preset vs2026-x64-debug
ctest --preset vs2026-x64-debug -R exploration_fixture_contracts
ctest --preset vs2026-x64-debug -R exploration_scaling
```

## Adding a fixture
1. Add a new folder under `tests/performance/exploration_fixtures/`.
2. Provide a data-only template at `tests/fixtures/world/templates/exploration_baseline.worlddef.json`.
3. Register the fixture in `tests/performance/exploration_fixtures/fixtures.json`.
4. Ensure the navigation script remains identical across fixtures.
