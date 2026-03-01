Status: ACTIVE
Version: 1.0.0
Owner: Core Engineering
Last Updated: 2026-03-01

# SpecSheet Constitution

## 1. Purpose
`SpecSheet` is the universal, typed, versioned standards substrate for engineering constraints and acceptance criteria across structures, interfaces, geometry, and operations.

`SpecSheet` is data-defined and deterministic. It is pack-driven and optional at runtime.

## 2. Core Contract
- SpecSheets define constraints and acceptance criteria.
- SpecSheets are not solvers.
- Compliance is evaluated by deterministic processes that emit fingerprinted proof artifacts.
- Authoritative mutation for spec binding/compliance state is process-only.
- Runtime must boot and run with zero spec packs.

## 3. Universal Spec Types (Examples)
- `spec.track`
- `spec.road`
- `spec.tunnel`
- `spec.bridge`
- `spec.pressure_vessel`
- `spec.vehicle_interface`
- `spec.docking_interface`

These are examples, not a closed ontology list.

## 4. Data Model Principles
- `spec_sheet` instances reference `spec_type_id`.
- Parameters are typed via `parameter_schema_id` on `spec_type`.
- Tolerance behavior is explicit via `tolerance_policy_id`.
- Compliance checks are explicit via `compliance_check_ids`.
- All artifacts include deterministic fingerprints.
- Extension maps are open for forward evolution.

## 5. Process and Proof Model

### 5.1 Authoritative Processes
- `process.spec_apply_to_target`
- `process.spec_check_compliance`

### 5.2 Compliance Result Artifact
- `compliance_result` is derived, deterministic, and fingerprinted.
- Result may be `pass`, `warn`, or `fail`.
- Strict contexts may refuse with `refusal.spec.noncompliant` when configured by check policy.

## 6. Integration Contracts
- MAT: spec binding on assembly graph nodes and structure instances.
- ABS: checks may reference state/hazard/schedule requirements as declared inputs.
- CTRL: plan execution may enforce or ignore compliance by policy; decisions log compliance outcomes.
- ED/inspection: snapshots expose compliance summary with epistemic-safe redaction.
- MOB (future): guide geometry and mobility constraints consume `SpecSheet` parameters through control/process paths.

## 7. Determinism Rules
- Tick-only evaluation; no wall-clock.
- Stable ordering for checks and result rows.
- Stable fingerprint generation over canonical payloads.
- No hidden mutation; no bypass around process runtime.

## 8. Optional Pack Rule
- Spec packs are optional content packs.
- If no spec sheets are loaded:
- runtime remains valid,
- compliance processes can return deterministic no-op/empty results,
- no mandatory realistic defaults are assumed.

## 9. Non-Goals
- No full stress solver implementation in this phase.
- No mobility guide geometry solver in this phase.
- No domain-specific hardcoding by vehicle/rail type in engine logic.
