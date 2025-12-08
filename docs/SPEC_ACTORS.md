# Actors and Species

- Species (`Species`) define metabolism and tolerances: body mass, per-second O₂/H₂O consumption, CO₂/waste production, heat output, and min/max pressure/temp plus O₂/CO₂ fraction limits. Register via `dactor_species_register`.
- Actors (`Actor`) embed species plus spatial context (environment or zone), optional parent aggregate, health/stamina (Q16.16 0..1), carried mass/volume placeholders, and a `knowledge_id` handle.
- Registry: `dactor_create` allocates an actor with given species/env; `dactor_get`/`destroy` manage lookup.
- Tick: `dactor_tick_all` computes per-tick life support from species rates (scaled by `g_domino_dt_s`). If inside a zone, it draws O₂ and emits CO₂/heat via `dzone_add_gas`/`dzone_add_heat`; otherwise it samples ambient defaults. Pressure/temp/O₂/CO₂ tolerances gate satisfaction; unsatisfied needs reduce health, satisfied slowly restores stamina. Fixed-point only; no floating point or randomness.
- Substance IDs for O₂/CO₂/H₂O can be configured via `dactor_set_substance_ids` to match the registered matter tables.
