# Authority and Omnipotence (OMNI0)

Status: binding.
Scope: canonical authority model, capability law, and omnipotence constraints.

## Purpose
Unify spectator, competitive, anarchy, and omnipotent control without modes or
hard-coded admin/cheat checks. Authority is data-defined, law-gated, and
auditable.

## Invariants
- Capabilities are additive and scoped.
- Law gates every authoritative action.
- Omnipotence never bypasses audit or archival rules.

## Authority Model
- All power is granted via capabilities.
- All restriction is enforced via law (including anti-cheat).
- Capabilities are additive; denials are explicit negative capabilities.
- Capabilities are scoped by domain, time window, and subject type.
- No layer implies another; every capability declares its layer coverage.

Authority layers are defined in `schema/authority/SPEC_AUTHORITY_LAYERS.md`.

## Intent -> Action -> Effect (Mandatory)
Every action, including omnipotent ones, follows:
1) Intent: declared capability and law targets.
2) Law Gate: capability and policy evaluation.
3) Effect: explicit, auditable operation.

Example:
Teleport player
- Intent: TRAVEL_FORCE
- Law target: AUTH.SPATIAL_OVERRIDE
- Effect: OP_TRAVEL_FORCE

No direct mutation is allowed outside this pipeline.

## Omnipotence (Still Law-Gated)
Omnipotence is the union of capabilities across layers. It does not bypass:
- law evaluation,
- audit requirements,
- archival and fork constraints.

History edits and archival mutations require a fork per EXIST2. Even
omnipotent actions must emit explicit effects and audit records.

## Audit and Explainability
Every authority outcome MUST explain:
- which capability granted or denied the action,
- which law targets and scopes were evaluated,
- which effect token was emitted.

## Forbidden assumptions
- "Admin" checks replace law and capability gating.
- Omnipotence implies unlimited, unaudited mutation.

## Dependencies
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`

## See also
- `schema/authority/SPEC_OMNIPOTENCE.md`
- `schema/capabilities/SPEC_CAPABILITY_TAXONOMY.md`
- `schema/capabilities/SPEC_NEGATIVE_CAPABILITIES.md`
- `schema/law/SPEC_LAW_KERNEL.md`
- `docs/architecture/AUTHORITY_IN_REALITY.md`
