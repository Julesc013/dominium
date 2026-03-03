# THERM_PHASE_CURE_BASELINE

Date: 2026-03-03  
Series: THERM-2

## Implemented Scope

1. Phase profile contract
- Added canonical phase profile schema for material threshold data.
- Added baseline material phase registry entries for water, iron, adhesive, and concrete stubs.

2. Curing state and process model
- Added cure state schema and deterministic `process.cure_state_tick`.
- Added model-driven cure increment + defect hazard behavior.

3. Insulation integration
- Added insulation constitutive model and T1 solve integration for effective conductance scaling.
- Added inspection summary for insulation effects.

4. Material phase transformation process
- Added deterministic `process.material_transform_phase` with provenance/event emission.
- Supports explicit byproduct batch emission under process input control.

5. Heat exchanger interface prep
- Added thermal/fluid stub port type declarations.
- Added machine type stub for heat exchanger interface composition.

6. Safety hooks
- Added overpressure hook emission path for gas transitions in sealed contexts.
- Added overtemp safety hook emission for out-of-range curing.

## Determinism And Governance

1. Phase/cure state mutation is process-only.
2. Model outputs are deterministic and ordered by stable IDs.
3. RepoX/AuditX hooks were extended for phase/cure anti-bespoke checks.

## FLUID-0 Readiness

1. Heat exchanger interface can be coupled to fluid network ports without ontology change.
2. Insulation and phase/cure contracts are now data-driven and compatible with constitutive-model extension.

## Gate Runs (2026-03-03)

1. RepoX
- Command: `python tools/xstack/repox/check.py --profile STRICT`
- Result: `pass` (18 warn findings; no refusal findings after topology regeneration).

2. AuditX
- Command: `python tools/auditx/auditx.py scan --repo-root . --format both`
- Result: `scan_complete` (global findings present in repo baseline; run succeeded).

3. TestX (THERM-2 required cases)
- Command: `python tools/xstack/testx/runner.py --profile FAST --subset test_phase_transition_trigger_deterministic --subset test_cure_progress_deterministic --subset test_insulation_modifies_conductance --subset test_phase_transform_emits_provenance --subset test_heat_exchanger_stub_exists`
- Result: `pass` (`selected_tests=5`, `findings=0`).

4. strict build
- Command: `python tools/xstack/run.py strict --repo-root . --cache on`
- Result: `refusal` due pre-existing global baseline failures outside THERM-2 scope (`compatx`, full-suite `testx`, packaging/session smoke). THERM-2 targeted gates above passed.

5. Topology map
- Command: `tools/governance/tool_topology_generate.cmd --repo-root .`
- Result: `complete`; updated `docs/audit/TOPOLOGY_MAP.json` and `docs/audit/TOPOLOGY_MAP.md`.
