# CIV0a Minimal Survival Loop

This document defines the CIV0a implementation surface for cohort survival.
It is deterministic, event-driven, and minimal by design.

## Goals
- Two humans can survive or die based on explicit actions.
- Consumption is scheduled by ACT events, not per-tick scans.
- Production is command-driven; no passive fabrication.
- Starvation/dehydration deaths are causal and deterministic.

## Data model summary
- Cohorts live in `game/rules/survival/cohort_model.*`.
- Needs state lives in `game/rules/survival/needs_model.*`.
- Consumption scheduling lives in `game/rules/survival/consumption_scheduler.*`.
- Production actions live in `game/rules/survival/survival_production_actions.*`.

## Event-driven consumption
- Each cohort has `next_due_tick`.
- Scheduler processes only due cohorts.
- Consumption updates hunger/thirst deterministically.
- Death hooks are emitted when thresholds are crossed.

## Production actions
- Actions are explicit commands (CMD0/CMD1).
- Completion is scheduled at ACT end_tick.
- Outputs add to food/water/shelter deterministically.
- Provenance refs are recorded on completion.

## LIFE integration
- Survival emits death hooks when starvation or dehydration occurs.
- Adapters must map these hooks to `life_handle_death(...)` or a LIFE2-approved bridge.
- Cohort count reduction is deterministic and bounded.

## Epistemic constraints
- Stores and thresholds are authoritative.
- UI receives only capability-filtered signals (e.g., "hungry" flags).
- No omniscient HUD counters are permitted.

## Determinism and scalability
- No global iteration over cohorts per tick.
- Batch vs step equivalence is enforced by tests.
- Macro scheduler hooks support FP3 integration.

## Tests
Required tests live in `game/tests/civ0a/dom_civ0a_survival_tests.cpp`:
- consumption determinism
- batch vs step equivalence
- starvation death trigger
- production completion
- no global iteration
