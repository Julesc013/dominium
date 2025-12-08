# Jobs / Tasks

- Job model: `Job { id, kind, state, target_tile, required_item, required_count, work_time_s, assigned_actor, deps[4], dep_count }`. Kinds include build/deconstruct/transport/operate/repair/research/custom. States: pending/assigned/in-progress/complete/cancelled/failed.
- Registry: `djob_create` (sequential IDs, bounded array), `djob_get`, `djob_cancel`, `djob_mark_complete`.
- Tick: `djob_tick` walks all jobs each tick. Pending jobs stay pending until assignment (deps checked for completion). In-progress jobs accumulate elapsed time via `g_domino_dt_s`; once elapsed ≥ `work_time_s`, they move to COMPLETE. No scheduling/pathfinding yet—this is scaffolding for higher-level systems.
- Deterministic, fixed-point only; no dynamic allocation during tick.
