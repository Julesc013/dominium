--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

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
# Research

- Tech nodes: `Tech { id, name, prereq[], research_time_s, science_item/count, unlocked_machines[], unlocked_recipes[] }`. Register via `dresearch_register_tech`.
- Progress state: `TechProgress { tech_id, progress_0_1, completed }` stored globally after `dresearch_init_progress(max_techs)`.
- Work application: `dresearch_apply_work(tech, science_units)` converts integer science units into progress (`units / science_count`), clamping at 1.0; if `science_count` is 0, tech completes immediately. `dresearch_tick` currently no-ops; labs will call `dresearch_apply_work` when recipes finish.
- Unlocking: completion status is tracked; game/mod layer enforces unlocks for machines/recipes based on `completed`.
- Deterministic, fixed-point only; no per-tick allocations after initialization.
