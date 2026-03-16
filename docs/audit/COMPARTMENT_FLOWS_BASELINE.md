Status: DERIVED
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: INT-2 Compartment Flows baseline completion report.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Compartment Flows Baseline

## Quantities Tracked
- Compartment macro/meso state is represented by `schema/interior/compartment_state.schema`:
  - `air_mass`
  - `water_volume`
  - `temperature` (optional)
  - `oxygen_fraction` (optional)
  - `smoke_density` (optional)
  - `derived_pressure` (derived deterministic value)
- Flow policy and templates are registry-driven:
  - `data/registries/compartment_flow_policy_registry.json`
  - `data/registries/portal_flow_template_registry.json`

## Portal Conductance Model
- `src/interior/compartment_flow_builder.py` builds deterministic FlowChannels from interior graph topology.
- Portal conductance is derived from:
  - portal template (`door_basic`, `hatch_basic`, `vent_basic`, `airlock_basic`)
  - per-portal overrides (`portal_flow_params`)
  - portal state machine state (`open|closed|vented|damaged|...`)
  - sealing coefficient and open-state multiplier
- Channels are generated in deterministic order by sorted volume/portal IDs and channel IDs.
- `src/interior/compartment_flow_engine.py` applies gradient-limited directional transfer to avoid same-tick bidirectional cancellation while preserving deterministic ordering.

## Leak Hazard Model
- Leak definitions are schema-driven via `schema/interior/leak_hazard.schema`.
- Leaks generate flow channels to deterministic outside boundary node (`interior.node.outside`) when present.
- Hazard integration uses `tick_hazard_models` with deterministic ordering and budget controls.
- Flow processing remains on FlowSystem substrate (`src/core/flow/flow_engine.py`) and emits transfer/loss artifacts.

## Diegetic Instruments and Alarms
- Observation and instrument channel integration includes:
  - `ch.diegetic.interior.pressure`
  - `ch.diegetic.interior.oxygen`
  - `ch.diegetic.interior.smoke_alarm`
  - `ch.diegetic.interior.flood_alarm`
  - `ch.diegetic.interior.alarm`
- These channels are registry-declared in `data/registries/instrument_type_registry.json` and surfaced with epistemic redaction.
- Coarse alarm bands (`OK/WARN/DANGER`) are derived per compartment from policy thresholds.

## Inspection and Overlay Integration
- Inspection sections integrated:
  - `section.interior.pressure_map`
  - `section.interior.flood_map`
  - `section.interior.portal_leaks`
- Render overlays expose deterministic procedural compartment/portal diagnostics without asset dependencies.

## Guardrails and Tests
- RepoX invariants integrated:
  - `INV-INTERIOR-FLOWS-USE-FLOWSYSTEM`
  - `INV-NO-ADHOC-CFD`
  - `INV-NO-TRUTH-LEAK-IN-INSTRUMENTS`
- AuditX analyzers integrated:
  - `CompartmentFlowDuplicationSmell` (`E98_COMPARTMENT_FLOW_DUPLICATION_SMELL`)
  - `InstrumentTruthLeakSmell` (`E99_INSTRUMENT_TRUTH_LEAK_SMELL`)
- INT-2 TestX coverage added and passing:
  - `test_flow_builder_deterministic`
  - `test_pressure_equalization_deterministic`
  - `test_flood_transfer_deterministic`
  - `test_portal_open_close_affects_flow`
  - `test_time_warp_large_dt_stable`
  - `test_epistemic_redaction_of_values`

## Gate Run Summary
- RepoX (`python tools/xstack/repox/check.py --profile STRICT`): PASS (1 warn; non-gating high-risk audit threshold warning)
- AuditX (`python tools/auditx/auditx.py verify --repo-root .`): run complete
- TestX INT-2 subset (`python tools/xstack/testx_all.py --profile FAST --cache off --subset ...`): PASS
- strict build (`python tools/xstack/run.py strict`): REFUSAL due pre-existing global CompatX/TestX/lab-build findings outside INT-2 scope; INT-2 registry compile/session/ui steps passed
- ui_bind (`python tools/xstack/ui_bind.py --check`): PASS

## Extension Points
- HVAC machinery integration through ACT ports (`port.material_in/out`, pumps/valves).
- Pump/valve process packs can tune conductance using portal flow params and policies.
- Future ROI-only CFD refinement can consume the same compartment state and flow artifacts without changing macro canonical model.
