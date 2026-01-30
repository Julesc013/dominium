# Exploration Scaling Proof (W1)

Status: binding evidence.
Scope: exploration navigation, camera, inspect, and renderer behavior.

## Constant-cost guarantee
Exploration actions (navigation, camera switching, inspect toggles, and
UI rendering) must remain constant-cost with respect to world size and depth.
World size may change only in inactive/collapsed content.

## Evidence
The following guards establish the constant-cost guarantee:

- **Fixture contracts**: `tests/perf/exploration_fixture_contracts.py`
  - Validates data-only fixtures and asserts identical navigation scripts.
  - Ensures fixtures differ only in topology size, not active content.

- **Scaling integration**: `tests/integration/exploration_scaling_tests.py`
  - Runs the same navigation script against all fixtures.
  - Compares derived exploration metrics for equality across fixtures.
  - Verifies identical replay hashes across fixtures and repeated runs.
  - Ensures camera/inspect do not mutate domain or position unexpectedly.
  - Enforces renderer parity across supported backends (null/soft/etc.).

- **Traversal guards**: `tests/integration/exploration_scale_guard_tests.py`
  - Confirms exploration paths do not parse or traverse topology data.
  - Prevents renderer traversal of the full universe.

## What is NOT guaranteed
- Wall-clock performance (frame time, GPU throughput, driver overhead).
- Asset streaming or pack loading costs.
- Server-side simulation or activity systems.
- Non-exploration gameplay or progression.

## Future system constraints
Any new system that touches exploration must:
- Emit deterministic events so metrics can be derived from logs.
- Respect collapse/expand boundaries (see `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`).
- Avoid topology-wide traversal in exploration paths.
- Preserve deterministic ordering and float policy constraints.

Violations of these rules must be rejected by TestX guards in W1.
