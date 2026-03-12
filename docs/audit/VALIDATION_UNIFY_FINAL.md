Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: release-pinned validation governance report

# Validation Unify Final

## Suite List

- `validate.schemas` -> `complete` via `compatx_schema_suite` (errors=0, warnings=0)
- `validate.registries` -> `complete` via `stability_registry_suite` (errors=0, warnings=0)
- `validate.contracts` -> `complete` via `semantic_contract_suite` (errors=0, warnings=0)
- `validate.packs` -> `complete` via `pack_verification_suite` (errors=0, warnings=0)
- `validate.negotiation` -> `complete` via `negotiation_suite` (errors=0, warnings=0)
- `validate.library` -> `complete` via `library_manifest_suite` (errors=0, warnings=1)
- `validate.time_anchor` -> `complete` via `time_anchor_suite` (errors=0, warnings=0)
- `validate.arch_audit` -> `complete` via `arch_audit_suite` (errors=0, warnings=0)
- `validate.determinism` -> `complete` via `determinism_scan_suite` (errors=0, warnings=0)

## Legacy Validators Mapped

- Total legacy/significant validation surfaces: `23`
- Active direct adapters: `11`
- Coverage/deprecation adapters: `12`

## Readiness

- `validate --all` is available through AppShell for governed products.
- Legacy validator surfaces are mapped to unified suites or explicitly deprecated with replacement targets.
- Readiness for UI mode selection and path virtualization passes: `yes`, subject to the current scoped validation report staying clean.
