--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Governance context, law layering, and enforcement rules.
SCHEMA:
- Governance record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No governance without institutions and law references.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_GOVERNANCE — Governance Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define governance as law layered on institutions, scoped to domains, and
backed by legitimacy and resources. Governance is configuration, not modes.

## Required fields
- governance_id (stable, unique within a timeline)
- domain_ref (spatial jurisdiction)
- institution_refs (enforcement bodies)
- law_profile_refs (law targets and policy bindings)
- legitimacy_ref (see SPEC_LEGITIMACY)
- resource_account_refs (enforcement budgets)
- provenance_refs (origin and causal chain)

Optional fields:
- policy_refs (local governance policy sets)
- escalation_refs (enforcement escalation paths)
- audit_refs (governance audit configuration)

## Rules (absolute)
- Governance is spatially scoped to domains; no global authority is implied.
- Governance requires institutions; no abstract bonuses are allowed.
- Law and capability gates remain mandatory; governance does not bypass them.
- Enforcement capacity scales with legitimacy and resources.

## Integration points
- Institutions: `schema/civ/SPEC_INSTITUTIONS.md`
- Legitimacy: `schema/civ/SPEC_LEGITIMACY.md`
- Authority layers: `schema/authority/README.md`
- Domain jurisdictions: `schema/domain/README.md`
- Law kernel: `schema/law/README.md`

## See also
- `docs/arch/GOVERNANCE_AND_INSTITUTIONS.md`
