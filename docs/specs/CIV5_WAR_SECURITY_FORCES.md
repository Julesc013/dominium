# CIV5 WAR1 — Security Forces & Military Cohorts

Status: draft
Version: 1

## Purpose
Define the CIV5-WAR1 implementation contract for deterministic, resource-backed
security forces. This is a game-layer implementation that consumes CIV0/CIV1/CIV2
systems and exposes event-driven readiness/morale schedules without combat logic.

## Scope (WAR1)
- Security forces as population-backed cohorts plus equipment.
- Readiness and morale state tracked deterministically and updated by events.
- Mobilization and demobilization pipelines with provenance.
- Epistemic visibility through estimates only.

## Canonical modules
- `game/rules/war/security_force.*`
- `game/rules/war/military_cohort.*`
- `game/rules/war/readiness_state.*`
- `game/rules/war/morale_state.*`
- `game/rules/war/mobilization_pipeline.*`
- `game/rules/war/demobilization_pipeline.*`

Public headers live in `game/include/dominium/rules/war/`.

## Determinism rules
- All registries are ordered by stable IDs.
- All readiness/morale changes are scheduled events only.
- Batch vs step equivalence must hold for readiness/morale schedules.
- No randomness or OS time in war rules.

## Integrations
- Population cohorts (CIV0/CIV0a): mobilization consumes cohort counts.
- Logistics (CIV1): equipment and supplies are consumed via stores/flows.
- Governance (CIV2): legitimacy and enforcement capacity gate mobilization.
- Epistemics (INF/EPIS): external observers receive estimates only.

## Refusal codes (WAR1)
- `INSUFFICIENT_POPULATION`
- `INSUFFICIENT_EQUIPMENT`
- `INSUFFICIENT_LOGISTICS`
- `INSUFFICIENT_AUTHORITY`
- `INSUFFICIENT_LEGITIMACY`

## Scheduling rules
- Readiness ramp-up and supply checks are due-scheduled events.
- Morale decay or legitimacy checks are due-scheduled events.
- Security forces expose `next_due_tick` derived from readiness/morale.

## Prohibitions
- No per-tick combat updates.
- No fabrication of personnel, equipment, or outcomes.
- No direct UI access to authoritative force state.

## Tests (WAR1)
Implemented in `game/tests/civ5_war1_security_force_tests.cpp`:
- Mobilization determinism.
- No fabrication on missing population/equipment.
- Readiness batch vs step equivalence.
- Demobilization conservation.
- Epistemic estimate gating.
