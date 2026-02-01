Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# CIV5 WAR3 — Occupation, Resistance, & Insurgency

Status: draft
Version: 1

## Purpose
Define the WAR3 implementation contract for deterministic occupation control,
resistance pressure, and disruption effects without random spawns or per-tick loops.

## Scope (WAR3)
- Territory control records and contested flags.
- Occupation maintenance with enforcement, legitimacy, and supply checks.
- Resistance pressure updates driven by deterministic thresholds.
- Disruption events applied to logistics capacity and stores.
- Enforcement attrition applied deterministically when resistance is active.
- Pacification policies with resource costs and scheduled effects.

## Canonical modules
- `game/rules/war/territory_control.*`
- `game/rules/war/occupation_state.*`
- `game/rules/war/resistance_state.*`
- `game/rules/war/resistance_scheduler.*`
- `game/rules/war/disruption_effects.*`
- `game/rules/war/pacification_policies.*`

Public headers live in `game/include/dominium/rules/war/`.

## Determinism rules
- All updates use integer math; no randomness or OS time.
- Occupation and resistance updates are scheduled via due events only.
- Disruption effects are deterministic capacity reductions (no RNG losses).

## Integrations
- CIV1 logistics: supply checks and store consumption.
- CIV2 governance: legitimacy thresholds and decay.
- CIV0a survival: deprivation signals from cohort needs.
- EPIS: estimates for control/resistance when capability is absent.

## Scheduling rules
- `next_due_tick` drives all occupation and resistance processing.
- No global iteration across territories.
- Disruption and policy effects fire only at scheduled ACT times.

## Prohibitions
- No random rebel spawns.
- No per-tick scans of territories.
- No omniscient occupation or resistance disclosure to UI.

## Tests (WAR3)
Implemented in `game/tests/civ5_war3_occupation_tests.cpp`:
- Deterministic occupation failure without supply.
- Deterministic resistance activation from legitimacy deficit.
- Deterministic disruption effects.
- Batch vs step equivalence for occupation timelines.
- No global iteration with many territories.