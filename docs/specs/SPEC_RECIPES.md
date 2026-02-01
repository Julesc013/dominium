Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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
# Recipes

- Definition: `Recipe { id, name, kind, time_s, power_in/out, heat_in/out, item_in/out[], fluid_in/out[], gas_in/out[], unlock_tech_id }` with fixed maxima per IO kind. Kinds: machine/research/environmental/custom.
- Items: `RecipeItemIO { item, count }`; Fluids/Gases: `RecipeFluidIO { substance, volume_m3 }` (Q48.16).
- Registry: `drecipe_register` stores templates; lookup via `drecipe_get`.
- Stepping: `drecipe_step_machine(Machine*, Recipe*, tick)` advances `Machine.progress_0_1` by `dt/time_s` (using `g_domino_dt_s`). Returns `RecipeStepResult { batch_started, batch_completed }`. Progress resets to 0 on completion; higher layers must move inputs/outputs when `batch_completed` is true.
- Deterministic, fixed-point only; no inventory movement inside recipe stepping—callers handle transfers and unlock checks.