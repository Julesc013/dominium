--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Institution formation, authority scopes, enforcement behavior.
SCHEMA:
- Institution record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No authority without explicit capability and law.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_INSTITUTIONS — Institution Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define institutions as organized rule-enforcing entities backed by resources
and legitimacy (governments, corporations, guilds, religions, militaries).

## Required fields
- institution_id (stable, unique within a timeline)
- institution_type (schema-defined)
- existence_state (EXIST0 state)
- domain_scope_refs (jurisdictional scope)
- authority_profile_ref (capabilities and law targets)
- legitimacy_ref (see SPEC_LEGITIMACY)
- resource_account_refs (inputs for enforcement/operations)
- governance_refs (governance contexts this institution serves)
- provenance_refs (origin and causal chain)

Optional fields:
- membership_refs (people, cohorts, orgs)
- infrastructure_refs (physical bases)
- policy_refs (internal rulebooks)

## Rules (absolute)
- Institutions require explicit formation effects and provenance.
- Authority is additive capability, not bypass.
- Enforcement capacity depends on resources and legitimacy.
- Institution scope is spatially bounded to domains.

## Integration points
- Governance: `schema/civ/SPEC_GOVERNANCE.md`
- Legitimacy: `schema/civ/SPEC_LEGITIMACY.md`
- Authority layers: `schema/authority/README.md`
- Law targets: `schema/law/README.md`
- Domains: `schema/domain/README.md`

## See also
- `docs/arch/GOVERNANCE_AND_INSTITUTIONS.md`
