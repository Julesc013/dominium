Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# VIS-3 Validation

Scope: tools/ + docs/visualization + docs/tools for VIS-3 (observation and tooling views).

Validation artifacts:
- `tools/tests/vis3_observability_tests.cpp` (headless, no assets)

Coverage matrix:
- Tools cannot mutate state: `test_immutability`
- Snapshots are immutable: `test_snapshot_access`
- Replay is deterministic: `test_determinism`
- Visualization works headless: `test_world_and_visualization`
- Inspection reveals no hidden authority: `test_snapshot_access`, `test_agent_institution_inspectors`
- Removing tools does not affect simulation: `test_immutability`

Notes:
- Tests are deterministic and avoid UI/render dependencies.