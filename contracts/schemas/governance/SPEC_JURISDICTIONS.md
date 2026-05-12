--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Jurisdiction rules, boundaries, and governance binding.
SCHEMA:
- Jurisdiction record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No global per-tick jurisdiction scans.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_JURISDICTIONS — Deterministic Jurisdictions (CIV2)

Status: draft  
Version: 1

## Purpose
Define jurisdiction records as first-class, deterministic governance domains.

## Jurisdiction schema
Required fields:
- jurisdiction_id
- boundary_ref (body/region/parcel set)
- default_time_standard_id (T4)
- default_money_standard_id (E2)
- policy_set_id
- enforcement_capacity_ref
- legitimacy_ref
- next_due_tick (ACT)

Rules:
- Jurisdictions are explicit constructions; no auto-spawn.
- next_due_tick is required for event-driven governance.

## Determinism requirements
- Jurisdiction IDs are stable and ordered.
- No per-tick global scans of jurisdictions.

## Integration points
- Legitimacy: `schema/governance/SPEC_LEGITIMACY.md`
- Policy system: `schema/governance/SPEC_POLICY_SYSTEM.md`
- Enforcement: `schema/governance/SPEC_ENFORCEMENT.md`
- Standard resolution: `schema/governance/SPEC_STANDARD_RESOLUTION_GOV.md`

## Prohibitions
- No hidden or implicit jurisdiction authority.
- No UI-driven jurisdiction state changes.
