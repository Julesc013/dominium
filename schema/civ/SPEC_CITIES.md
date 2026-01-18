--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- City rules, governance context usage, and building membership.
SCHEMA:
- City record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No auto-spawn of cities or buildings.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_CITIES — City Model (CIV1)

Status: draft  
Version: 1

## Purpose
Define the deterministic city structure used for bounded infrastructure and
production scheduling.

## City schema
Required fields:
- city_id
- location_ref (body/region)
- building_ids (bounded list)
- population_cohort_refs (bounded list)
- governance_context_ref

Optional fields:
- boundary_ref
- next_due_tick (if city-level scheduling is required)

Rules:
- building_ids are bounded and deterministically ordered.
- population_cohort_refs are bounded and deterministically ordered.

## Determinism requirements
- City membership MUST be deterministic and auditable.
- City updates MUST be event-driven (buildings drive scheduling).
- No global per-city update loops are allowed.

## Integration points
- Buildings/machines: `schema/civ/SPEC_BUILDINGS_MACHINES.md`
- Production chains: `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- Logistics flows: `schema/civ/SPEC_LOGISTICS_FLOWS.md`
- Population cohorts: `schema/civ/SPEC_POPULATION_COHORTS.md`

## Prohibitions
- No auto-spawn or implicit city creation.
- No per-tick global scans of all cities.
