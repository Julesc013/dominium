Status: DRAFT
Version: 1.0.0-draft
Last Reviewed: 2026-02-14
Compatibility: Derived from `schema/authority/authority_context.schema` v1.1.0 and canon v1.0.0.

# AuthorityContext Contract

## Purpose
Define the runtime authority envelope required to evaluate intents lawfully.

## Source of Truth
- Schema: `schema/authority/authority_context.schema`
- Related: `docs/architecture/AUTHORITY_MODEL.md`, `docs/contracts/law_profile.md`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Intended Contract Fields (Required)
- `authority_context_id: id`
- `authority_origin: enum(client|server|tool|replay)`
- `experience_id: id`
- `law_profile_id: id`
- `entitlements: [id]`
- `capability_set_hash: tag`
- `epistemic_scope_id: id`
- `privilege_watermark_policy: enum(none|observer|dev)`
- `audit_required: bool`
- `server_authoritative: bool`
- `refusal_policy_id: id`
- `extensions: map`

## Invariants
- Intents without a valid authority context must be refused.
- Authority context does not create capability; it binds resolved capability/law context for evaluation.
- `authority_origin` is explicit and auditable.
- `server_authoritative=true` does not bypass law; it selects authority location.
- Epistemic scope and watermark policy must be carried through observation surfaces.
- `extensions` must preserve unknown keys.

## Example
```yaml
authority_context:
  authority_context_id: authority.lab.observer
  authority_origin: client
  experience_id: experience.lab
  law_profile_id: law.lab.observe_only
  entitlements:
    - client.ui.map
    - client.ui.timeline
  capability_set_hash: caphash.7f09...
  epistemic_scope_id: epistemic.lab.sensor_limited
  privilege_watermark_policy: observer
  audit_required: true
  server_authoritative: false
  refusal_policy_id: refusal.default
  extensions: {}
```

## TODO
- Add explicit lifecycle ownership for context negotiation between launcher/client/server.
- Add refusal matrix keyed by field-level validation failure.
- Add deterministic hashing rule for `capability_set_hash` materialization.

## Cross-References
- `docs/contracts/law_profile.md`
- `docs/contracts/refusal_contract.md`
- `docs/architecture/observation_kernel.md`

