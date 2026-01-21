--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Household membership rules and authority usage.
SCHEMA:
- Household record format and versioning metadata.
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No global partner matching or household scans.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_HOUSEHOLDS — Bounded Household Model (CIV0)

Status: draft  
Version: 1

NOTE: Legacy CIV1 spec. Superseded by CIV0+ canonical documents in
`schema/civ/README.md` and `schema/economy/README.md`. Retained for reference
and non-authoritative if conflicts exist.

## Purpose
Define the bounded household model used to constrain authority queries and
eligibility without global scans.

## Household schema
Required fields:
- household_id (stable)
- residence_ref (region/body or shard key)
- resource_pool_ref (food/shelter pool reference)
- members (bounded list of person_ids)
- next_due_tick (optional; ACT)

Rules:
- member list MUST be bounded and deterministically ordered.
- household size limits are enforced (no unbounded growth).

## Determinism requirements
- Membership updates MUST be deterministic.
- Authority queries MUST be bounded by household membership.
- No global search for eligible partners or heirs.

## Integration points
- LIFE control authority: `schema/life/SPEC_CONTROL_AUTHORITY.md`
- Population cohorts: `schema/civ/SPEC_POPULATION_COHORTS.md`
- Event-driven stepping: `docs/SPEC_EVENT_DRIVEN_STEPPING.md`

## Prohibitions
- No global scans for pairing or eligibility.
- No household creation based on UI/camera state.
