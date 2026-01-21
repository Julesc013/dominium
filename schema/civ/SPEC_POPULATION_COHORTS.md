--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Cohort rules, bucket semantics, and population updates.
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
# SPEC_POPULATION_COHORTS — Population Cohorts (CIV0)

Status: draft  
Version: 1

NOTE: Legacy CIV1 spec. Superseded by CIV0+ canonical documents in
`schema/civ/README.md` and `schema/economy/README.md`. Retained for reference
and non-authoritative if conflicts exist.

## Purpose
Define the deterministic cohort data model used for population scaling in CIV0.

## Cohort key and identity
Required fields:
- cohort_key:
  - body_id
  - region_id (or shard/region key)
  - org_id (optional; 0 means none)
- cohort_id (stable, deterministic; derived from cohort_key)

Rules:
- cohort_id MUST be deterministically derived from cohort_key.
- cohort_id MUST be stable across runs and replays.

## Cohort state (authoritative)
Required fields:
- count
- age_buckets (fixed, bounded array)
- sex_buckets (fixed, bounded array; UNKNOWN allowed)
- health_buckets (fixed, bounded array)
- needs_state_ref (ties to CIV0a needs)
- next_due_tick (ACT)
- provenance_summary_hash

Bucket invariants:
- Sum(age_buckets) == count
- Sum(sex_buckets) == count
- Sum(health_buckets) == count

## Determinism requirements
- Cohort ordering is stable (sorted by cohort_id).
- Updates MUST be event-driven via next_due_tick (no per-tick scans).
- Bucket adjustments are deterministic and use fixed tie-break ordering.

## Integration points
- CIV0a needs: `schema/civ/SPEC_NEEDS_MINIMAL.md`
- LIFE births/deaths: `schema/life/SPEC_BIRTH_LINEAGE_OVERVIEW.md`, `schema/life/SPEC_DEATH_AND_ESTATE.md`
- Event-driven stepping: `docs/SPEC_EVENT_DRIVEN_STEPPING.md`
- Interest sets and fidelity: `docs/SPEC_INTEREST_SETS.md`, `docs/SPEC_FIDELITY_PROJECTION.md`

## Prohibitions
- No global iteration over all cohorts each tick.
- No fabricated cohort growth without causal pipelines.
- No unordered bucket iteration without deterministic normalization.
