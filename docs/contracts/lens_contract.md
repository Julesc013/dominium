Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/lens.schema.json` v1.0.0 and CompatX `tools/xstack/compatx/version_registry.json`.

# Lens Contract

## Purpose
Define canonical lens payload requirements for deterministic observation transformation.

## Source of Truth
- Schema: `schemas/lens.schema.json` (`version: 1.0.0`)
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Required Fields (`v1.0.0`)
- `schema_version` (`const "1.0.0"`)
- `lens_id` (string)
- `lens_type` (`diegetic|nondiegetic`)
- `transform_description` (string)
- `required_entitlements` (array of strings)
- `epistemic_constraints` (object with deterministic observation limits)

## Invariants
- Lens contracts transform perception only and cannot mutate truth.
- `lens_type` remains explicit and law/authority-gated.
- Entitlement requirements are data-declared and auditable.
- Unknown top-level fields are refused by strict validation.
- Observation refusal codes for lens gating are deterministic:
  - `LENS_FORBIDDEN`
  - `ENTITLEMENT_MISSING`

## Example JSON (`schemas/lens.schema.json`)
```json
{
  "schema_version": "1.0.0",
  "lens_id": "lens.diegetic.sensor",
  "lens_type": "diegetic",
  "transform_description": "Filters truth model to cockpit-grade instrument output.",
  "required_entitlements": [
    "ui.sensor",
    "ui.map"
  ],
  "epistemic_constraints": {
    "visibility_policy": "sensor_limited",
    "max_resolution_tier": 2
  }
}
```

## TODO
- Add compatibility notes for future lens category expansions.
- Add persisted PerceivedModel projection schema for per-lens snapshot caches.
- Add schema-level linkage to presentation matrix once matrix schema is formalized.

## Cross-References
- `docs/contracts/law_profile.md`
- `docs/contracts/refusal_contract.md`
- `docs/contracts/versioning_and_migration.md`
- `docs/architecture/observation_kernel.md`
- `docs/architecture/lens_system.md`
