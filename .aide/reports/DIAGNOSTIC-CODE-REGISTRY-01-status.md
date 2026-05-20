# DIAGNOSTIC-CODE-REGISTRY-01 Status

Branch: `main`

Starting HEAD: `3fa25f5e20464e5b31fc138bd0bd704b7c6cd677`

Origin/main at start: `3fa25f5e20464e5b31fc138bd0bd704b7c6cd677`

Ending HEAD: pending commit.

## Created Or Updated

- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/diagnostics/diagnostic_code.schema.json`
- `contracts/diagnostics/diagnostic_severity.registry.json`
- `contracts/diagnostics/diagnostic_category.registry.json`
- `contracts/diagnostics/diagnostic_policy.contract.toml`
- `contracts/evidence/evidence_packet.schema.json`
- `contracts/evidence/evidence_ref.schema.json`
- `contracts/event/event.schema.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/command/command_surface.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `tools/validators/contracts/check_diagnostics_registry.py`
- `tests/contract/diagnostics/**`
- `docs/architecture/diagnostics_and_evidence.md`
- `docs/development/diagnostic_code_guidelines.md`
- AIDE reports and repo audit/status docs.

## Registry Summary

- Diagnostic codes registered: 14.
- Severities registered: 7.
- Categories registered: 26.
- Stability: all initial diagnostic codes are provisional.
- Public surface registry updated: yes.
- Command/refusal registry updated: yes, by narrow diagnostic/evidence references.

## Scope Guard

No runtime diagnostic dispatch, Workbench UI, package behavior, gameplay,
renderer, native GUI, release publication, tag, upload, or full CTest proof was
implemented.

## Validation Summary

- Diagnostic validator: PASS, 14 codes, 7 severities, 26 categories, 0 errors, 0 warnings.
- Diagnostic fixture validation: PASS.
- Public surface validator: PASS, 47 surfaces.
- Command surface validator: PASS.
- Dependency direction validator: FAIL on known existing debt, 358 violations and 38 warnings.
- Fast strict: PASS, 32/32 commands, 351.282 seconds.

## Result

PASS_WITH_WARNINGS pending final commit.

Known warnings remain dependency-direction debt, ABI warning debt, and T4
full/release proof debt.

Next task: `ARTIFACT-IDENTITY-LAW-01`.
