--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT scheduling primitives and stable ID allocation.
GAME:
- Reincarnation policy, authority validation, and embodiment rules.
SCHEMA:
- Reincarnation contract formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No default reincarnation without an explicit contract.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_REINCARNATION — Reincarnation Contract Canon

Status: draft
Version: 1

## Purpose
Define data-defined reincarnation/respawn policies. Reincarnation is not the
default and must be explicitly allowed by contract.

## ReincarnationContract (conceptual)
Required fields:
- reincarnation_contract_id
- allowed_identity_continuity (same_identity | new_identity | forbidden)
- memory_retention (full | partial | none)
- location_rules_ref
- delay_rules_ref (ACT-based)
- authority_scope_ref
- provenance_ref

Optional fields:
- jurisdiction_ref
- embodiment_rules_ref (clone | drone | avatar | other)
- notes_ref (non-sim)

## Rules (absolute)
- Hardcore: reincarnation forbidden unless explicitly allowed by contract.
- Softcore: reincarnation allowed only via contract and authority.
- Spectator: no life entity bound to the controller.
- Reincarnation must emit explicit effects and audit records.

## Identity continuity
If `same_identity` is allowed:
- identity_state remains ACTIVE,
- lineage records include a continuity marker,
- embodiment is recreated via an explicit pipeline.

If `new_identity` is allowed:
- a new life_id is created,
- lineage records reference the prior identity as ancestor,
- prior identity remains unchanged.

## Integration points
- Continuation policies: `schema/life/SPEC_CONTINUATION_POLICIES.md`
- Identity and lineage: `schema/life/SPEC_IDENTITY_AND_LINEAGE.md`
- Death contracts: `schema/life/SPEC_DEATH_CONTRACTS.md`
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
