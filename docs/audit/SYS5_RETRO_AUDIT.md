Status: DERIVED
Last Reviewed: 2026-03-06
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: SYS-5 retro-consistency audit for certification workflow integration.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SYS5 Retro Audit

## Existing SPEC Checks
- `process.spec_check_compliance` already writes deterministic `spec_compliance_results` rows with graded outcomes.
- Runtime helpers (`_latest_spec_compliance_result_for_target`, `_spec_compliance_summary_for_target`) already provide deterministic target-scoped lookup.
- SPEC type registration is already enforced by `data/registries/spec_type_registry.json` and system interface validation.

## Existing Safety Validation Inputs
- System-level invariant validation (`src/system/system_validation_engine.py`) already checks required safety pattern presence from invariant templates.
- Safety patterns are registered centrally in `data/registries/safety_pattern_registry.json`.
- Domain safety outputs already exist in ELEC/THERM/FLUID process/runtime pathways and can be consumed as certification evidence.

## Implicit System-Level Spec Checks Found
- Template instantiation currently validates that template `spec_bindings.spec_type_id` values are registered.
- SYS collapse/expand validates interface and invariants, but has no unified certificate issuance/revocation lifecycle.
- No canonical `process.system_evaluate_certification` exists yet.

## Migration Plan to Unified SYS Certification Engine
- Add canonical SYS certification schemas:
  - `certification_profile`
  - `certification_result`
  - `certificate_artifact`
- Add deterministic system certification engine:
  - evaluate interface/invariants/spec/safety/degradation checks
  - issue CREDENTIAL artifact only on pass
  - always emit REPORT summary
- Integrate invalidation hooks:
  - collapse/expand material graph changes
  - degradation threshold breach
  - spec compliance fail/violation
- Add proof hashes:
  - certification_result_hash_chain
  - certificate_artifact_hash_chain
  - revocation_hash_chain
- Add RepoX/AuditX enforcement and SYS-5 TestX regression coverage.
