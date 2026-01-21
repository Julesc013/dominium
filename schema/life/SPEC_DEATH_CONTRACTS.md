--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT scheduling primitives and stable ID allocation.
GAME:
- Death triggers, cause rules, and authority validation.
SCHEMA:
- Death contract formats, outcomes, and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No silent despawn of identity.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_DEATH_CONTRACTS — Death Contract Canon

Status: draft
Version: 1

## Purpose
Define explicit, deterministic death contracts. Death is an effect, not a
background process.

## DeathContract (conceptual)
Required fields:
- death_contract_id
- life_type (INDIVIDUAL | COHORT | ABSTRACT_POPULATION | SYNTHETIC_AGENT)
- cause_rules_ref (natural | violent | systemic | other)
- timing_rules_ref (ACT-based)
- authority_scope_ref
- domain_scope_ref
- provenance_ref

Optional fields:
- jurisdiction_ref
- estate_rules_ref
- remains_rules_ref
- notes_ref (non-sim)

## Death outcomes (mandatory)
- DEATH_ACCEPT
- DEATH_DEFER
- DEATH_REFUSE

Refusal requires an explicit refusal code and audit trail.

## Rules (absolute)
- No life entity removal without a DeathContract.
- Death must be scheduled on ACT.
- Identity persists after death; only embodiment or population counts change.
- Death must emit audit records and provenance.

## Integration points
- Death and estate records: `schema/life/SPEC_DEATH_AND_ESTATE.md`
- Life entities: `schema/life/SPEC_LIFE_ENTITIES.md`
- Reality flow: `docs/arch/REALITY_FLOW.md`

## See also
- `schema/life/SPEC_IDENTITY_AND_LINEAGE.md`
