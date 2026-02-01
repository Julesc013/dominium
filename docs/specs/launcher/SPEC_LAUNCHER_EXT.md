Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `launcher/`.

GAME:
- None. This spec is implemented under `launcher/`.

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
# Launcher Extensions

Launcher extensions let mods/packs add tabs, canvases, or custom actions to the
Dominium launcher. They piggyback on the Domino mod ABI and are loaded alongside
regular content.

## ABI
- Header: `include/domino/mod.h`
- Struct: `dom_launcher_ext_v1 {struct_size, struct_version, on_launcher_start,
  on_register_views, on_action(action_id,payload), on_build_canvas(inst,
  canvas_id, dom_gfx_buffer*)}`.
- Entry point: mods export `const dom_launcher_ext_v1* dom_get_launcher_ext_v1()`.
- Registration helpers exposed to the runtime:
  - `dom_launcher_ext_register(core, ext)` — register an extension with the
    current `dom_core`.
  - `dom_launcher_ext_count/core` + `dom_launcher_ext_get` — enumerate
    registered extensions.

## Lifecycle
1. Launcher creates `dom_core` and `dom_launch_ctx`.
2. During launch creation, all registered extensions receive:
   - `on_launcher_start(core)` once.
   - `on_register_views(core)` to add views via `dom_view_register`.
3. Front-ends may forward string actions through
   `dom_launch_handle_custom_action(ctx, action_id, payload)` which broadcasts
   to `on_action`.
4. When a canvas build is requested and not handled by built-ins
   (`world_surface`, etc.), `on_build_canvas` is queried; returning `true`
   treats the canvas as handled.

## View registration
- Extensions call `dom_view_register(core, dom_view_desc*)` during
  `on_register_views` to add custom tabs/panels. These surface through
  `dom_ui_list_views` and can be rendered by launcher front-ends.

## Canvas hooks
- Custom canvases expose complex dashboards/graphs. If a view's `model_id`
  matches the canvas id, the launcher will call `dom_canvas_build`, which in
  turn calls `on_build_canvas` for unknown ids.

## Actions
- UI elements can trigger custom actions identified by strings
  (`"stats.refresh"`, `"server.list"`). Front-ends call
  `dom_launch_handle_custom_action(ctx, action_id, payload)`; extensions decide
  whether to handle the payload.

## Notes
- Extensions stay deterministic and local; no dynamic OS API calls from the
  launcher. A later revision can add manifest flags to mark mods as launcher
  extensions explicitly.
- An example stub lives under `data/mods/examples/launcher_example/` with a
  simple canvas/view registration.