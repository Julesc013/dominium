Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# META-INSTR0 Retro Audit

Status: AUDIT COMPLETE  
Date: 2026-03-07  
Scope: instrumentation-like features, epistemic/control bypass risks, and missing instrumentation surfaces.

## Existing Instrument-Like Features

- `data/registries/instrument_type_registry.json`
  - Existing diegetic instrument channels and update processes (`instr.*` family).
- `src/diegetics/instrument_kernel.py`
  - Diegetic readout synthesis surface used by observation pipeline.
- `tools/xstack/sessionx/observation.py`
  - Channel-gated readout projection path (`ch.diegetic.*`).
- `src/pollution/measurement_engine.py`
  - Deterministic pollution measurement artifact production.
- `src/meta/explain/explain_engine.py` and `data/registries/explain_contract_registry.json`
  - Forensics/explain generation + contract registry.
- Existing AuditX/TestX instrumentation checks:
  - `tools/auditx/analyzers/e99_instrument_truth_leak_smell.py`
  - `tools/xstack/testx/tests/test_no_truth_access_in_instruments.py`
  - `tools/xstack/testx/tests/test_instrument_redaction.py`

## Bypass / Consistency Risks Found

- No single owner-bound instrumentation surface declaration exists for:
  - control points
  - measurement points
  - forensics endpoints
- Access controls are fragmented:
  - interface signal `access_policy_id` exists in SYS interface validation,
  - but there is no shared instrumentation access-policy registry for measurement/control endpoints.
- Measurement model semantics are fragmented:
  - calibration + readout exist,
  - but no normalized measurement model registry for uncertainty/precision policy across system/process owners.
- Existing instrument coverage is channel-centric (`instr.*`) rather than owner-centric (system/capsule/process/domain binding).

## Missing Instrumentation Surfaces (Current Gap)

- ELEC networks:
  - breaker and isolator control points are not declared in a unified instrumentation surface registry.
  - voltage/current/PF measurement points are not owner-declared in one place.
- THERM networks:
  - thermal controls/measurements are not surfaced through a unified owner instrumentation contract.
- FLUID networks:
  - valve/isolation controls and pressure/flow readouts lack owner-level instrumentation declarations.
- CHEM/PROC:
  - process start/stop + yield/defect/QC instrumentation points are not unified under one instrumentation surface contract.
- SYS macro capsules:
  - policy-gated “request expand”, boundary measurements, and forced-expand/system-failure forensics are not unified as instrumentation surfaces.

## Migration Notes

- Keep existing diegetic instrument kernel and domain process paths unchanged.
- Add a new meta-level instrumentation surface registry and engine that references existing action templates, explain contracts, and measurement flows.
- Enforce owner-bound declarations incrementally:
  - STRICT warning first for missing owner instrumentation declarations.
