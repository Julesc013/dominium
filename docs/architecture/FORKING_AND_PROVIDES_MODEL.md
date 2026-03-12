Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Forking And Provides Model (LIB-5)

Status: binding.
Scope: deterministic pack namespacing, provider declarations, instance-scoped provider choices, and PACK-COMPAT / CAP-NEG integration.

## Purpose

LIB-5 defines how multiple forks, versions, and alternative ecosystems coexist without implicit winner selection.

The model enables:

- forks of packs without `pack_id` collision
- multiple providers for the same semantic surface
- deterministic instance-scoped provider choice
- strict refusal for ambiguity-sensitive installs and servers
- stable sharing, cloning, and portable export/import

No silent provider selection is permitted.

## Namespace Rules

Canonical new pack id forms:

- `official.<org>.<pack>`
- `mod.<author>.<pack>`
- `fork.<origin_pack_id>.<fork_author>.<fork_name>`
- `local.<user>.<pack>`

Rules:

- `pack_id` is stable and unique.
- forks must not reuse the origin pack_id.
- fork ids keep the origin in-band through `fork.<origin_pack_id>.<fork_author>.<fork_name>`.
- legacy reverse-DNS pack ids remain loadable for compatibility but are not reused for new fork identities.

## Provides Declarations

A pack may advertise one or more provider surfaces through deterministic declarations:

- `provides_id`
- `provides_type`
- optional `priority`
- optional required contract ranges
- optional required capabilities
- compatibility notes in `extensions`

Canonical `provides_type` values:

- `domain`
- `dataset`
- `template_set`
- `ui_pack`
- `protocol_extension`

Multiple packs may declare the same `provides_id`.

## Resolution Policies

Instances and pack verification resolve required `provides_id` values through one deterministic policy:

- `resolve.strict_refuse_ambiguous`
- `resolve.explicit_required`
- `resolve.deterministic_highest_priority`
- `resolve.deterministic_lowest_pack_id`

Policy semantics:

- `resolve.strict_refuse_ambiguous`: refuse if more than one provider exists.
- `resolve.explicit_required`: the instance must declare `chosen_pack_id`.
- `resolve.deterministic_highest_priority`: pick the highest `priority`, tie-break by `pack_id`.
- `resolve.deterministic_lowest_pack_id`: pick the lexicographically lowest `pack_id`.

Strict servers must refuse ambiguous providers.
All provider selections are logged in canonical resolution records or in the bound pack lock.

## Pack Verification Integration

PACK-COMPAT must:

1. gather `provides_declarations` and `required_provides_ids`
2. determine `resolution_policy_id`
3. resolve providers deterministically
4. refuse `refusal.provides.ambiguous` or `refusal.provides.missing_provider` when needed
5. pin `provides_resolutions` and provider-implied capabilities into the verified lock

Required provider choice becomes part of the lock identity. Pack identity itself remains stable; provider choice is recorded separately in the lock and/or instance resolution record.

## Capability Negotiation Integration

If a chosen provider implies required capabilities:

- those capabilities join the CAP-NEG input set
- unsupported dependent features must degrade deterministically or refuse
- no capability surface may be silently enabled or silently disabled

## Invariants

- `INV-FORKS-MUST-NAMESPACE`
- `INV-PROVIDES-RESOLUTION-DETERMINISTIC`
- `INV-STRICT-REFUSES-AMBIGUITY`

## Related Contracts

- `schema/lib/provides_declaration.schema`
- `schema/lib/provides_resolution.schema`
- `schema/packs/pack_lock.schema`
- `schema/packs/pack_compat_manifest.schema`
- `docs/architecture/PACK_FORMAT.md`
