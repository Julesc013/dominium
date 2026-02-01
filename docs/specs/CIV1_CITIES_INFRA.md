Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# CIV1 Cities, Infrastructure, and Production

This document defines the CIV1 infrastructure layer: deterministic cities,
building machines, production chains, and logistics flows. All processing is
event-driven and scheduled in ACT time.

## Core components

- Cities (`schema/civ/SPEC_CITIES.md`)
  - Bounded building lists and cohort references.
  - Buildings drive scheduling; cities do not tick globally.
- Building machines (`schema/civ/SPEC_BUILDINGS_MACHINES.md`)
  - Inputs/outputs are explicit store references.
  - Production uses scheduled start/complete events.
- Production recipes (`schema/civ/SPEC_PRODUCTION_CHAINS.md`)
  - Inputs/outputs are ordered by asset_id.
  - Duration is ACT-based only.
- Logistics flows (`schema/civ/SPEC_LOGISTICS_FLOWS.md`)
  - Flow arrivals are scheduled and deterministic.
  - Capacity is enforced explicitly.

## Event-driven production

- Machines schedule a start when inputs are available.
- Completion occurs at start + duration_act.
- Outputs are produced only at completion.
- Maintenance degrades deterministically; if too low, production halts.

No per-tick scanning of machines is allowed.

## Logistics

- Goods move via flows (not vehicles yet).
- Flows consume inputs at departure and deliver at arrival_act.
- Capacity is reserved and released deterministically.

## Determinism and scaling

- All registries are ordered by stable IDs.
- Batch vs step equivalence is required for production and logistics.
- Processing is bounded to due events only.

## Epistemic constraints

Knowledge of production and inventories is capability-gated.
UI must not assume omniscient city dashboards.

## CI enforcement

The following IDs in `docs/CI_ENFORCEMENT_MATRIX.md` cover CIV1:

- CIV1-PROD-DET-001
- CIV1-BATCH-001
- CIV1-LOG-DET-001
- CIV1-NOGLOB-001
- CIV1-FID-001
