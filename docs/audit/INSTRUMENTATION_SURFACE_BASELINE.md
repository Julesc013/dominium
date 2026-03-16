Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# INSTRUMENTATION_SURFACE_BASELINE

## Scope
- Series: `META-INSTR-0`
- Objective: establish a uniform instrumentation surface contract across `system|capsule|process|domain` owners for control, measurement, and forensics endpoints.

## Registry Baseline
- `data/registries/instrument_type_registry.json`
  - Includes `instrument.multimeter`, `instrument.thermometer`, `instrument.pressure_gauge`, `instrument.pollution_sensor`, `instrument.logic_probe`, `instrument.logic_analyzer`.
  - `logic_*` and newly introduced instrumentation channels are explicitly marked `runtime_status: stub` for follow-up runtime channel surfacing.
- `data/registries/measurement_model_registry.json`
  - `meas.default_quantized`
  - `meas.calibrated_basic`
  - `meas.lab_high_precision`
- `data/registries/access_policy_registry.json`
  - `access.physical_contact_required`
  - `access.role_required`
  - `access.admin_only`
- `data/registries/instrumentation_surface_registry.json`
  - Surface owners: 6
  - Control points: 12
  - Measurement points: 12
  - Forensics points: 11
  - Owners:
    - `domain.elec`
    - `domain.therm`
    - `domain.fluid`
    - `domain.chem`
    - `process.proc.default`
    - `capsule.system.default`

## Engine Baseline
- `src/meta/instrumentation/instrumentation_engine.py` provides:
  - deterministic instrumentation surface resolution by owner key
  - control access validation (`AuthorityContext` + access policy + physical access)
  - measurement observation generation (`OBSERVATION` family) with instrument-required gating and deterministic redaction
  - deterministic forensics routing through explain engine contracts with redaction policy handling
- Engine is read-only with respect to truth state (no authoritative mutation path).

## Enforcement Baseline
- RepoX:
  - `INV-SYSTEM-MUST-DECLARE-INSTRUMENTATION` (STRICT warn, FULL fail policy)
  - `INV-NO-TRUTH-READOUT-WITHOUT-INSTRUMENT`
- AuditX:
  - `E302_OMNISCIENT_READOUT_SMELL` (`OmniscientReadoutSmell`)
  - `E303_MISSING_INSTRUMENTATION_SURFACE_SMELL` (`MissingInstrumentationSurfaceSmell`)

## TestX Baseline
Added and passing in STRICT subset:
- `test_instrumentation_surface_schema_valid`
- `test_access_policy_enforced`
- `test_measurement_redaction_applied`
- `test_forensics_routes_to_explain_engine`
- `test_no_truth_leak_in_diegetic_mode`

## Gate Snapshot (run during META-INSTR0 finalization)
- `RepoX STRICT`: **not pass** (pre-existing cross-series refusals remain outside `META-INSTR-0` scope).
- `AuditX verify --changed-only`: completed; findings emitted.
- `TestX STRICT subset (META-INSTR0 tests)`: pass.
- `strict build`: full stack strict runner timed out in this workspace; no green strict-build signal obtained in this pass.
- Topology map: regenerated (`docs/audit/TOPOLOGY_MAP.json`, `docs/audit/TOPOLOGY_MAP.md`).

## Readiness
- Instrumentation contract, schemas, registries, baseline bindings, engine support, enforcement, and core tests are in place.
- Ready for LOGIC debugging tool wiring and channel surfacing follow-up (`META-INSTR-1` / LOGIC series integration).
