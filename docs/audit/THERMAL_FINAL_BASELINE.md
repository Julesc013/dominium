Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# THERMAL_FINAL_BASELINE

Date: 2026-03-04
Series: THERM-5

## Scope Completed

1. Deterministic thermal stress envelope
- Deterministic scenario generator:
  - `tools/thermal/tool_generate_therm_stress_scenario.py`
- Deterministic stress harness:
  - `tools/thermal/tool_run_therm_stress.py`
- Deterministic replay verifier:
  - `tools/thermal/tool_replay_therm_window.py`

2. Deterministic degradation behavior
- Canonical degradation order:
  1. `degrade.therm.tick_bucket`
  2. `degrade.therm.t0_budget`
  3. `degrade.therm.defer_noncritical_models`
  4. `degrade.therm.fire_spread_cap`
- All degrade decisions emit DecisionLog rows and RECORD artifacts.

3. Proof and replay integration
- Added thermal proof hash chains:
  - `thermal_network_state_hash_chain`
  - `heat_input_hash_chain`
  - `fire_cascade_hash_chain`
- Existing thermal proof chains retained:
  - `thermal_network_hash`
  - `overheat_event_hash_chain`
  - `fire_state_hash_chain`
  - `ignition_event_hash_chain`
  - `fire_spread_hash_chain`
  - `runaway_event_hash_chain`

4. Regression lock
- Added `data/regression/therm_full_baseline.json`
- Update tag required: `THERM-REGRESSION-UPDATE`

## Stress Results Summary

Reference scenario:
- scenario id: `scenario.therm.stress.85f4064b339c`
- seed: `7705`
- budget envelope: `therm.envelope.standard`
- ticks: `48`

Observed:
- max temperature observed: `129`
- total overtemp trips: `0`
- total downgraded networks: `0`
- total fire events: `94`
- proof window replay match: `true`
- full proof summary match: `true`

Additional baseline fingerprints:
- representative building cooling scenario
- runaway scenario
- downgrade-pressure scenario

## Envelope Guarantees

- Cost-unit budgeting only; no wall-clock coupling.
- Downgrades are explicit and logged; no silent degrade path.
- Fire spread remains bounded and deterministic.
- Heat inputs are logged and hash-chain auditable.

## Gate Run Summary

RepoX:
- `python tools/xstack/repox/check.py --profile STRICT`
- status: `pass`

AuditX:
- `python tools/xstack/auditx/check.py --profile STRICT`
- status: `pass` (warnings present)

TestX (THERM-5 targeted set):
- `python tools/xstack/testx_all.py --profile STRICT --cache off --subset test_stress_scenario_deterministic --subset test_degradation_order_deterministic --subset test_proof_hash_chain_stable --subset test_replay_window_hash_match --subset test_null_boot_unchanged`
- status: `pass`

Strict build gate:
- `python tools/xstack/run.py strict`
- status: `refusal` due pre-existing repository-wide STRICT issues outside THERM-5 scope (CompatX/session boot/packaging lab validation).

Topology map:
- `python tools/governance/tool_topology_generate.py --repo-root .`
- status: `complete`
- fingerprint: `ec40f7c7ebf5962dbdc0d2b166de4008ae282436e322beb6b3a74e28760b9ee2`

## Readiness Checklist For FLUID-0

1. Thermal stress envelope is deterministic and bounded.
2. Loss-to-heat inputs are logged and proof-chained.
3. Cascade boundedness holds under stress.
4. Regression lock exists with governance tag.
5. Scenario generation, stress run, and replay verification tooling is in place.
