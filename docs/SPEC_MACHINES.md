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
# Machines

- Types: `MachineType { id, name, family, casing_material, idle/active/max power, ports[], default_recipe_id }` registered via `dmachine_type_register`. Families cover assembler/smelter/refinery/pump/generator/battery/life-support/lab/thruster/custom.
- Ports: `MachinePortDesc { port_index, kind, net_kind, item_filter, substance_filter }`, up to `DMACH_MAX_PORTS` per type. Port kinds span item/fluid/gas/power/heat/signal/data directions; `net_kind` references `NetKind` for network integration.
- Instances: `Machine { id, type_id, agg, element, progress_0_1, efficiency_0_1, health_0_1, recipe_id, power_draw_W, power_output_W, flags }`. Instances attach to aggregates/elements.
- Tick: `dmachine_tick_all` walks instances. Each machine chooses idle/active power; if enabled and a recipe is set, it steps via `drecipe_step_machine`, updates progress, and reports power draw/output. Inventory and network transfers are handled by higher layers later.
- Control: `dmachine_set_recipe` selects a recipe (resets progress); `dmachine_set_enabled` gates simulation.
