Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Deprecation And Quarantine

Status: Canonical (ARCH-REF-1, superseded in detail by ARCH-REF-4)
Version: 1.1.0

Superseding references:
- `docs/architecture/DEPRECATION_LIFECYCLE.md`
- `docs/architecture/ADAPTER_PATTERN.md`

## Deprecation Registry
- Deprecations are declared canonically via:
  - `schema/governance/deprecation_entry.schema`
  - `schema/governance/deprecation_registry.schema`
  - `data/governance/deprecations.json`
- Runtime or schema identifiers being phased out must be registered with:
  - `deprecated_id`
  - `replacement_id`
  - `reason`
  - `removal_target_version`
  - `status`

## Quarantine Directory Policy
- `legacy/` and `quarantine/` are temporary quarantine areas only.
- Quarantine content must not be referenced by production/runtime code paths.
- Adapter-only access is allowed when adapter paths are explicitly declared in `data/governance/deprecations.json`.
- AuditX and RepoX enforce non-reference policy.

## Migration Requirements
For each deprecation/refactor:
1. Identify overlap and selected replacement abstraction.
2. Provide adapter/shim only when needed for deterministic compatibility.
3. Register deprecation entry.
4. Add deterministic equivalence tests before and after migration.
5. Add or tighten RepoX enforcement to block regressions.
