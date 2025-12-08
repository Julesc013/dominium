# Research

- Tech nodes: `Tech { id, name, prereq[], research_time_s, science_item/count, unlocked_machines[], unlocked_recipes[] }`. Register via `dresearch_register_tech`.
- Progress state: `TechProgress { tech_id, progress_0_1, completed }` stored globally after `dresearch_init_progress(max_techs)`.
- Work application: `dresearch_apply_work(tech, science_units)` converts integer science units into progress (`units / science_count`), clamping at 1.0; if `science_count` is 0, tech completes immediately. `dresearch_tick` currently no-ops; labs will call `dresearch_apply_work` when recipes finish.
- Unlocking: completion status is tracked; game/mod layer enforces unlocks for machines/recipes based on `completed`.
- Deterministic, fixed-point only; no per-tick allocations after initialization.
