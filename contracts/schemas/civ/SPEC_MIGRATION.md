--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Migration rules, cause codes, and flow scheduling.
SCHEMA:
- Migration flow record format and versioning metadata.
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No random wandering or implicit migration.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_MIGRATION — Population Migration Flows (CIV0)

Status: draft  
Version: 1

NOTE: Legacy CIV1 spec. Superseded by CIV0+ canonical documents in
`schema/civ/README.md` and `schema/economy/README.md`. Retained for reference
and non-authoritative if conflicts exist.

## Purpose
Define deterministic, event-driven migration flows for population movement.

## Migration flow schema
Required fields:
- flow_id (stable)
- src_cohort_key
- dst_cohort_key
- count_delta (non-negative)
- start_act
- arrival_act
- cause_code
- provenance_mix (or reference)

Rules:
- Migration is modeled as flows, not per-agent movement.
- arrival_act MUST be scheduled in ACT (no wall-clock time).
- Flow ordering is deterministic; apply with stable ordering on flow_id.

## Determinism requirements
- Flow creation is deterministic from inputs.
- Application is deterministic and updates cohort buckets consistently.
- Batch vs step equivalence MUST hold for flow arrivals.

## Integration points
- Cohorts: `schema/civ/SPEC_POPULATION_COHORTS.md`
- Event-driven stepping: `docs/SPEC_EVENT_DRIVEN_STEPPING.md`
- Interest sets: `docs/SPEC_INTEREST_SETS.md`

## Prohibitions
- No global migration scans per tick.
- No random migration or stochastic wandering.
- No direct mutation outside cohort authority domains.
