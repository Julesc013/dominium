--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Organization formation, membership, and operational rules.
SCHEMA:
- Organization record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit organization creation.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_ORGANIZATIONS — Organization Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define organizations as membership-based entities that coordinate production,
logistics, defense, or social functions. Organizations may or may not be
institutions; institutions are rule-enforcing by definition.

## Required fields
- organization_id (stable, unique within a timeline)
- organization_type (schema-defined)
- existence_state (EXIST0 state)
- membership_refs (people, cohorts, institutions)
- asset_refs (resources, infrastructure, settlements)
- provenance_refs (origin and causal chain)

Optional fields:
- authority_profile_ref (when organization has explicit authority)
- governance_ref (if organization participates in governance)
- operational_domain_refs (areas of activity)

## Rules (absolute)
- Organizations require explicit formation effects and provenance.
- Organizations do not grant authority unless explicitly assigned capabilities.
- Membership changes are event-driven and auditable.

## Integration points
- Institutions: `schema/civ/SPEC_INSTITUTIONS.md`
- Governance: `schema/civ/SPEC_GOVERNANCE.md`
- Economy actors: `schema/economy/SPEC_ECONOMIC_ACTORS.md`
- Life entities: `schema/life/SPEC_LIFE_ENTITIES.md`

## See also
- `docs/arch/GOVERNANCE_AND_INSTITUTIONS.md`
