Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CHEM-1 Retro Consistency Audit

Status: AUDIT
Last Updated: 2026-03-05
Scope: CHEM-1 preflight over existing THERM combustion stubs, process runtime burn paths, and PHYS-3 energy-ledger discipline.

## 1) Existing Combustion Paths

Current combustion behavior is implemented in THERM/process layers:

- `src/models/model_engine.py`
  - `model_type.therm_combust_stub`
  - model outputs include deterministic `fuel_consumed`, `heat_emission`, and pollutant stub values.
- `src/thermal/network/thermal_network_engine.py`
  - deterministic model binding/evaluation for `model.therm_combust_stub`.
- `tools/xstack/sessionx/process_runtime.py`
  - `process.start_fire`
  - `process.fire_tick`
  - `process.end_fire`
  - authoritative fuel decrement and fire event emission.

No dedicated CHEM reaction engine exists in the current baseline.

## 2) Direct Fuel Burn Logic Audit

Detected direct burn logic in canonical process handler:

- `process.fire_tick` computes:
  - `fuel_consumed`
  - `heat_emission`
  - `pollutant_emission`
  - `fuel_remaining` updates

Assessment:

- process-only mutation invariant is currently preserved.
- however, combustion profile/reaction profile formalization is not yet represented as CHEM reaction registry rows.

## 3) Energy Injection Bypass Audit

Combustion heat currently records to PHYS-3 ledger via:

- `_record_energy_transformation_in_state(...)`
- `transformation_id = "transform.chemical_to_thermal"`

Assessment:

- no direct bypass of energy ledger was found in active fire-tick path.
- `transform.chemical_to_electrical` hook is not yet registered.

## 4) Emission and POLL Readiness Audit

Current pollutant outputs:

- `thermal_pollutant_stub_rows` are emitted deterministically.
- no dedicated CHEM emission pool or pollutant tagging schema is present.

Assessment:

- deterministic emission logging exists at stub level.
- POLL handoff contract requires explicit CHEM-facing emission artifacts.

## 5) Explain/Proof Coverage Audit

Current proof/reporting status:

- fire hash chains exist (`fire_state`, `ignition`, `spread`, `runaway`).
- control proof bundle already carries energy/momentum hash chains.
- dedicated CHEM-1 chains (`combustion_hash_chain`, `emission_hash_chain`) are not yet present.

Current explain status:

- no combustion-specific explain contracts (`explain.combustion`, `explain.explosion`, `explain.low_efficiency`) are registered.

## 6) Migration Notes (CHEM-1)

Planned migration without intentional gameplay semantics change:

1. Keep `process.fire_tick` as canonical mutation path (no direct runtime bypass).
2. Add CHEM reaction profile registry for combustion/explosive stubs.
3. Add efficiency model factors (temperature + entropy + mixture ratio stub) as deterministic computation with explicit outputs.
4. Preserve `transform.chemical_to_thermal` ledger pathway; add optional `transform.chemical_to_electrical` hook.
5. Emit explicit combustion/emission RECORD artifacts suitable for future POLL consumption.
6. Extend proof surfaces with combustion/emission hash chains while retaining existing fire chains.

## 7) Deprecation Entries

Transitional paths to keep temporarily:

- `thermal_pollutant_stub_rows`
  - status: transitional
  - target: CHEM emission pool rows + pollutant-tagged RECORD artifacts.
- THERM-only combustion profile interpretation
  - status: transitional
  - target: CHEM reaction profile-backed combustion chain with deterministic compatibility behavior.
