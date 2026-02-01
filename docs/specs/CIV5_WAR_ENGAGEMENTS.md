Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# CIV5 WAR2 — Engagement Resolution & Casualties

Status: draft
Version: 1

## Purpose
Define the WAR2 implementation contract for deterministic, event-driven
engagement resolution and casualty generation. This layer resolves engagements
to outcomes without real-time combat or per-tick loops.

## Scope (WAR2)
- Engagement records and outcomes.
- Due-scheduled resolution at `resolution_act`.
- Deterministic loss accounting and casualty generation.
- Epistemic outcome summaries with uncertainty.

## Canonical modules
- `game/rules/war/engagement.*`
- `game/rules/war/engagement_scheduler.*`
- `game/rules/war/engagement_resolution.*`
- `game/rules/war/casualty_generator.*`
- `game/rules/war/loss_accounting.*`

Public headers live in `game/include/dominium/rules/war/`.

## Determinism rules
- Engagement order and resolution are stable and deterministic.
- Resolution uses integer math only; no randomness or OS time.
- Batch vs step equivalence holds for scheduler advances.

## Integrations
- LIFE2/LIFE4: casualties generated through `life_handle_death`.
- CIV1: supply consumption and equipment losses are recorded deterministically.
- CIV2: legitimacy deltas applied at resolution time.
- EPIS: estimates returned when capability is absent.

## Scheduling rules
- Engagements are registered with `next_due_tick = resolution_act`.
- Resolution fires only on due events.
- No per-tick combat processing.

## Prohibitions
- No real-time physics combat.
- No per-entity combat ticks.
- No omniscient outcome disclosure to UI.

## Tests (WAR2)
Implemented in `game/tests/civ5_war2_engagement_tests.cpp`:
- Deterministic resolution.
- Batch vs step equivalence.
- Casualty conservation.
- Logistics depletion effects.
- Epistemic delay estimates.