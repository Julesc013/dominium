# CIV5 WAR4 — Interplanetary & Interstellar Warfare

Status: draft
Version: 1

## Purpose
Define the WAR4 implementation contract for large-scale conflict control across
planetary and interstellar routes without fleet physics or global iteration.

## Scope (WAR4)
- Route control records with access policies.
- Blockade states and maintenance checks.
- Interdiction operations scheduling WAR2 engagements.
- Siege effects driven by CIV0a deprivation signals.
- Event-driven scheduling via a macro due scheduler.

## Canonical modules
- `game/rules/war/route_control.*`
- `game/rules/war/blockade.*`
- `game/rules/war/convoy_security.*`
- `game/rules/war/interdiction.*`
- `game/rules/war/siege_effects.*`
- `game/rules/war/war_scale_scheduler.*`

Public headers live in `game/include/dominium/rules/war/`.

## Determinism rules
- No randomness; integer math only.
- No per-tick scans of routes or domains.
- All updates depend on `next_due_tick`.

## Integrations
- CIV4 logistics: route control and blockade effects applied to flows.
- WAR2: interdictions schedule engagements deterministically.
- CIV0a survival: siege deprivation uses cohort needs.
- CIV2 governance: legitimacy decays under siege and blockade.
- EPIS: route and blockade knowledge is epistemically gated.

## Scheduling rules
- Blockades, interdictions, and sieges register with `war_scale_scheduler`.
- Due events only; no global iteration over all routes.

## Prohibitions
- No fleet physics or combat simulation.
- No random interdictions.
- No omniscient blockade or route safety maps.

## Tests (WAR4)
Implemented in `game/tests/civ5_war4_scale_tests.cpp`:
- Deterministic blockade effects.
- Interdiction scheduling determinism.
- Siege deprivation batch vs step equivalence.
- No global iteration with many routes.
- Deterministic shard message ordering.
