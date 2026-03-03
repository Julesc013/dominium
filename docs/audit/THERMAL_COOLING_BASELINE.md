# THERM-3 Thermal Cooling Baseline

## Scope
- Phase: `THERM-3` (Cooling systems, heat sinks/radiators, ambient coupling).
- Tier target: `T1` deterministic graph solve with ambient boundary coupling; `T0` bookkeeping fallback.
- Runtime constraints upheld:
  - no wall-clock use
  - no CFD/airflow solver
  - model-engine dispatch for cooling behaviors
  - process/log-first safety hooks

## Ambient Coupling Rules
- Boundary nodes are resolved from thermal node extensions (`boundary_to_ambient=true`).
- Ambient temperature inputs are sampled deterministically per node from:
  1. explicit `ambient_temperature_by_node`
  2. mapped field rows (`ambient_field_rows`)
  3. fallback constant ambient.
- Ambient exchange is model-driven (`model.therm_ambient_exchange`) with deterministic outputs:
  - `derived.therm.ambient_exchange`
  - `derived.therm.ambient_delta_energy`
- Solve outputs now include:
  - `ambient_exchange_rows`
  - `ambient_exchange_hash`
  - `ambient_eval_stride`
  - `ambient_deferred_count`

## Radiator Model
- Radiator/heat-sink behavior is model-driven (`model.therm_radiator_exchange`).
- Profiles resolve via `radiator_profile_registry`:
  - `radiator.passive_basic`
  - `radiator.forced_basic`
- Forced cooling uses deterministic multiplier selection through binding parameters (`forced_cooling_on`, `forced_cooling_multiplier`).
- Radiator exchanges are emitted separately as `radiator_exchange_rows` and hashed into `ambient_exchange_hash`.

## Insulation Interaction
- Insulation factor (`insulation_factor_permille`) scales effective coupling for both ambient and radiator exchange.
- Coupling policy defaults are registry-backed (`ambient.default`, `ambient.insulated`, `ambient.exposed`).
- Insulation effects are observable via thermal inspection summary sections and deterministic exchange deltas.

## Safety Integration
- Cooling insufficiency escalates existing thermal safety path:
  - `hazard.overheat` creation
  - `safety.overtemp_trip` event emission
- Repeated overtemp events can escalate to thermal runaway hook:
  - `hazard.thermal_runaway`
  - `safety.thermal_runaway`
- Hazard/safety registry coverage added for thermal cooling failure flows.

## UX and Inspection
- New inspection sections:
  - `section.thermal.ambient_exchange_summary`
  - `section.thermal.radiator_efficiency`
- Existing graph-level thermal inspection sets now include these sections for macro/meso/micro graph views.
- Summaries expose deterministic, policy-safe cooling state:
  - exchange totals
  - ambient averages
  - cooling stride/deferred counts
  - forced vs passive radiator utilization

## Multiplayer/Proof Coupling
- Proof bundle now carries cooling evidence via:
  - `ambient_exchange_hash`
- Existing thermal proof surfaces remain:
  - `thermal_network_hash`
  - `overheat_event_hash_chain`
- This supports deterministic lockstep verification for ambient/radiator outcomes.

## Enforcement
- RepoX rules added:
  - `INV-NO-ADHOC-COOLING`
  - `INV-THERM-AMBIENT-THROUGH-MODEL`
- AuditX analyzers added:
  - `InlineCoolingSmell` (`E199_INLINE_COOLING_SMELL`)
  - `DirectTemperatureAmbientSmell` (`E200_DIRECT_TEMPERATURE_AMBIENT_SMELL`)

## TestX Coverage (THERM-3)
- `test_ambient_exchange_deterministic`
- `test_radiator_cools_node`
- `test_insulation_reduces_heat_loss`
- `test_overheat_when_no_cooling`
- `test_budget_degrade_ambient_eval`

All above passed in explicit FAST subset execution.

## Gate Run Summary (2026-03-03)
- RepoX STRICT: `pass` (warnings present; no refusal).
- AuditX STRICT: `pass` (warnings present).
- TestX (THERM-3 subset): `pass` (5/5).
- Strict build (`python tools/xstack/run.py ... strict`): `error`
  - blocked by pre-existing pipeline issues outside THERM-3 scope:
    - CompatX refusal findings
    - session boot smoke refusal
    - broader TestX suite failures
    - packaging file-lock error (`WinError 32`)
- Topology map: updated via governance tool; outputs regenerated:
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/TOPOLOGY_MAP.md`

## Readiness for FLUID-0
- Thermal side of ambient exchange and radiator/heat-sink behavior is now deterministic and registry-driven.
- Heat exchanger coupling remains interface-compatible through existing THERM-2 stubs and model dispatch.
- Cooling baseline is ready for fluid-side exchanger coupling in FLUID-0 without introducing bespoke thermal branches.
