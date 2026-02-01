Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Actors and Species

- Species (`Species`) define metabolism and tolerances: body mass, per-second O₂/H₂O consumption, CO₂/waste production, heat output, and min/max pressure/temp plus O₂/CO₂ fraction limits. Register via `dactor_species_register`.
- Actors (`Actor`) embed species plus spatial context (environment or zone), optional parent aggregate, health/stamina (Q16.16 0..1), carried mass/volume placeholders, and a `knowledge_id` handle.
- Registry: `dactor_create` allocates an actor with given species/env; `dactor_get`/`destroy` manage lookup.
- Tick: `dactor_tick_all` computes per-tick life support from species rates (scaled by `g_domino_dt_s`). If inside a zone, it draws O₂ and emits CO₂/heat via `dzone_add_gas`/`dzone_add_heat`; otherwise it samples ambient defaults. Pressure/temp/O₂/CO₂ tolerances gate satisfaction; unsatisfied needs reduce health, satisfied slowly restores stamina. Fixed-point only; no floating point or randomness.
- Substance IDs for O₂/CO₂/H₂O can be configured via `dactor_set_substance_ids` to match the registered matter tables.