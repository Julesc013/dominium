Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Deprecation Framework Baseline

## Scope
ARCH-REF-4 establishes deterministic deprecation lifecycle governance, quarantine enforcement, and adapter-validated migration workflow.

## Lifecycle Summary
- States: `active`, `deprecated`, `quarantined`, `removed`
- Canonical registry: `data/governance/deprecations.json`
- Core schemas:
  - `schema/governance/deprecation_entry.schema`
  - `schema/governance/deprecation_registry.schema`

## Quarantine Rules
- `legacy/` and `quarantine/` are non-production zones.
- Runtime code must not import/reference these zones.
- Access is adapter-only and must be declared in deprecation registry.
- Build boundary scanner enforces quarantine policy and CMake linkage exclusion checks.

## Adapter Pattern Summary
- Adapter contract documented in `docs/architecture/ADAPTER_PATTERN.md`.
- Template available at `templates/adapter_template.md`.
- Registry-declared adapters:
  - `tools/governance/adapters/deprecation_registry_adapter.py`
  - `tools/governance/adapters/deprecation_schema_adapter.py`

## Validation and Tooling
- `tools/governance/tool_deprecation_check.py`
  - validates registry structure, ordering, fingerprint, adapter paths, removed-reference policy.
- `tools/governance/tool_migration_report.py`
  - generates `docs/audit/MIGRATION_STATUS.md`.

## RepoX Enforcement
- `INV-DEPRECATION-REGISTRY-VALID`
- `INV-NO-NEW-USE-OF-DEPRECATED`
- `INV-ADAPTER-ONLY-ACCESS`
- `INV-NO-PRODUCTION-LEGACY-IMPORT`

## AuditX Coverage
- `E112_LEGACY_IMPORT_SMELL` (LegacyImportSmell)
- `E113_DEPRECATED_USAGE_SMELL` (DeprecatedUsageSmell)
- `E114_ADAPTER_MISSING_SMELL` (AdapterMissingSmell)
- `E115_REMOVED_STILL_REFERENCED_SMELL` (RemovedStillReferencedSmell)

## TestX Coverage
- `test_deprecation_registry_deterministic`
- `test_no_production_import_from_quarantine`
- `test_deprecation_tool_reports_errors`

## Determinism and Runtime Safety
- Governance-only artifacts; no simulation semantic changes.
- No wall-clock dependency added.
- No runtime dependency on XStack/governance tooling paths.
