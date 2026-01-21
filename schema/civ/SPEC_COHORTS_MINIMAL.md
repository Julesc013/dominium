--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Cohort definitions, consumption policy, and survival rules.
SCHEMA:
- Cohort record format and versioning metadata.
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No global per-tick cohort scans.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_COHORTS_MINIMAL — Cohort Canon (CIV0a)

Status: draft  
Version: 1

NOTE: Legacy CIV1 spec. Superseded by CIV0+ canonical documents in
`schema/civ/README.md` and `schema/economy/README.md`. Retained for reference
and non-authoritative if conflicts exist.

## Purpose
Define the minimal cohort data model required for the CIV0a survival loop.

## Cohort schema (minimal)
Required fields:
- cohort_id (stable)
- count
- location_ref (region/body)
- next_due_tick (ACT)

Optional fields:
- person_ids (micro-mode only)
- age_bucket (cohort distribution)
- health_bucket (cohort distribution)

## Determinism requirements
- Cohort IDs are stable and deterministic.
- No iteration over all cohorts each tick.
- Consumption is scheduled via next_due_tick.

## Integration points
- Event-driven stepping: `docs/SPEC_EVENT_DRIVEN_STEPPING.md`
- Interest sets: `docs/SPEC_INTEREST_SETS.md`
- Fidelity projection: `docs/SPEC_FIDELITY_PROJECTION.md`
