--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT scheduling primitives and stable ID allocation.
GAME:
- Birth triggers, resource checks, and authority validation.
SCHEMA:
- Birth contract formats, outcomes, and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No spontaneous births.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_BIRTH_CONTRACTS — Birth Contract Canon

Status: draft
Version: 1

## Purpose
Define explicit, deterministic birth contracts. Birth is an effect, not a
background process.

## BirthContract (conceptual)
Required fields:
- birth_contract_id
- life_type (INDIVIDUAL | COHORT | ABSTRACT_POPULATION | SYNTHETIC_AGENT)
- parent_requirements_ref (optional for synthetic/abstract)
- environment_requirements_ref
- resource_requirements_ref
- timing_rules_ref (ACT-based)
- output_identity_rules_ref
- authority_scope_ref
- provenance_ref

Optional fields:
- jurisdiction_ref
- domain_scope_ref
- notes_ref (non-sim)

## Birth outcomes (mandatory)
- BIRTH_ACCEPT
- BIRTH_DEFER
- BIRTH_REFUSE

Refusal requires an explicit refusal code and audit trail.

## Rules (absolute)
- No life entity creation without a BirthContract.
- Birth must be scheduled on ACT (no per-tick scans).
- Birth must update population models deterministically.
- Birth must emit lineage and provenance records.

## Integration points
- Life entities: `schema/life/SPEC_LIFE_ENTITIES.md`
- Population models: `schema/life/SPEC_POPULATION_MODELS.md`
- Existence states: `schema/existence/SPEC_EXISTENCE_STATES.md`
- Reality flow: `docs/architecture/REALITY_FLOW.md`

## See also
- `schema/life/SPEC_IDENTITY_AND_LINEAGE.md`
