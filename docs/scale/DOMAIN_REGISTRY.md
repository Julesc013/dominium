Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schema/scale/domain_registry.schema` and `schemas/domain_foundation_registry.schema.json`.

# Domain Registry

## Purpose
Define the authoritative shape and governance of `data/registries/domain_registry.json`.

## Format
Top-level record:
- `schema_id`
- `schema_version`
- `records[]`

Each domain row includes:
- identity (`domain_id`, `human_name`, `description`)
- capability linkage (`required_capabilities`, `provided_capabilities`)
- structural declaration (`fields_declared`, `processes_declared`, `scope_tags`)
- solver compatibility (`solver_kinds_allowed`)
- contract linkage (`contract_ids`)
- lifecycle status (`status`, `deprecated`, `version_introduced`)
- `extensions`

## Naming Discipline
- Domain IDs are namespaced: `dom.domain.<namespace>.<name>`.
- IDs are stable and never reused.
- Renaming/removal requires explicit compatibility action.

## Versioning Rules
- Registry schema is semver-driven.
- Breaking field changes require version bump and migration/refusal path.
- Contract/dependency changes require deterministic validation updates.

## Deprecation Rules
- Deprecated rows remain present with `deprecated=true` and `status=deprecated`.
- Removal from registry without compatibility action is forbidden.

## Forward Compatibility
- Extensions must be explicit maps (`extensions`) and never silent implied defaults.
- Unknown top-level fields are refused by strict schema validation.

## TODO
- Add machine-readable deprecation policy timeline.
- Add explicit compatibility class mapping to CompatX report format.

## Cross-References
- `docs/scale/DOMAIN_MODEL.md`
- `docs/scale/CONTRACTS_AND_CONSERVATION.md`
- `schema/scale/domain_registry.schema`
- `schemas/domain_foundation_registry.schema.json`
