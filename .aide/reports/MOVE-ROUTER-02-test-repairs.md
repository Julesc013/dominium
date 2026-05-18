# MOVE-ROUTER-02 Test Repairs

Status: PARTIAL
Generated: 2026-05-18

## Applied

- Repaired the exploration scale guard fixture path to
  `tests/fixtures/world/templates/exploration_baseline.worlddef.json`.
- Updated the client shell exploration baseline loader to prefer the routed repo
  fixture while preserving the fixture-local fallback used by performance tests.
- Repaired XStack plan registry paths from old `data/registries` forms to
  `contracts/registry` forms.
- `test_gate_fast_strict_full_profiles.py --case full_shards_groups`: PASS.

## Remaining

- Focused RepoX is blocked by stale ruleset discovery.
- Broader TestX failed 140 of 344 lanes during the build-triggered suite.
- Remaining failures are concentrated in stale registry/pack paths, import
  package fallout, old source path expectations, and frozen hash drift.
