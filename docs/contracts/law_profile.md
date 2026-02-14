Status: DRAFT
Version: 1.0.0-draft
Last Reviewed: 2026-02-14
Compatibility: Derived from `schema/law/law_profile.schema` v1.2.0 and canon v1.0.0.

# LawProfile Contract

## Purpose
Define profile-driven legal behavior using declarative capability, entitlement, epistemic, and refusal bindings.

## Source of Truth
- Schema: `schema/law/law_profile.schema`
- Related: `docs/architecture/MODES_AS_PROFILES.md`, `docs/architecture/AUTHORITY_MODEL.md`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Intended Contract Fields (Registry)
`law_profile_registry` requires:
- `registry_id: id`
- `registry_version: semver`
- `schema_version_ref: tag`
- `profiles: [law_profile]`
- `extensions: map`

## Intended Contract Fields (Profile)
`law_profile` requires:
- `law_profile_id: id`
- `capabilities_granted: [id]`
- `capabilities_revoked: [id]`
- `entitlements_granted: [id]`
- `epistemic_policy_id: id`
- `allowed_intent_families: [id]`
- `forbidden_intent_families: [id]`
- `persistence_rules: [id]`
- `allowed_lenses: [id]`
- `forbidden_lenses: [id]`
- `watermark_policy: enum(none|observer|dev)`
- `audit_required: bool`
- `refusal_codes: [id]`
- `extensions: map`

## Invariants
- LawProfile is data, not a runtime mode branch.
- Capabilities grant attempts only; law gates determine outcomes.
- Lens allow/deny sets must align with authority and presentation contracts.
- Unknown fields under `extensions` must be preserved.
- Field rename/removal requires MAJOR schema bump and migration/refusal route.

## Example
```yaml
law_profile:
  law_profile_id: law.lab.observe_only
  capabilities_granted:
    - capability.observe
  capabilities_revoked:
    - capability.mutate
  entitlements_granted:
    - client.ui.timeline
  epistemic_policy_id: epistemic.lab.sensor_limited
  allowed_intent_families:
    - intent.observe
  forbidden_intent_families:
    - intent.mutate
  persistence_rules:
    - persistence.standard
  allowed_lenses:
    - lens.diegetic.sensor
  forbidden_lenses:
    - lens.nondiegetic.admin
  watermark_policy: observer
  audit_required: true
  refusal_codes:
    - REFUSE_LAW_FORBIDDEN
    - REFUSE_CAPABILITY_MISSING
  extensions: {}
```

## TODO
- Add compatibility matrix examples for MINOR vs MAJOR law profile changes.
- Add contract checks that detect contradictory allow/forbid intent family sets.
- Add governance examples for controlled rollout of profile revisions.

## Cross-References
- `docs/contracts/lens_contract.md`
- `docs/contracts/refusal_contract.md`
- `docs/architecture/pack_system.md`

