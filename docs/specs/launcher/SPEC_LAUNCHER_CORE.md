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
# Launcher Core

The launcher core is a reusable, UI-agnostic controller that sits on top of
`dom_core`/`dom_view`/`dom_canvas` and the `dsys` process layer. CLI/TUI/GUI
front-ends call this layer instead of reaching into platform or renderer
details.

## Public API
- Header: `include/dominium/launch_api.h`
- Context: `dom_launch_ctx` is opaque; created with `dom_launch_create` from a
  `dom_launch_desc {struct_size/struct_version = 1, core, ui_mode,
  product_id, version}`.
- Snapshot: `dom_launch_snapshot {struct_size/struct_version = 1, state,
  current_instance, current_package, current_view_id}` filled by
  `dom_launch_get_snapshot`.
- Actions: `dom_launch_handle_action(ctx, action, param_u32, param_str)` drives
  the state machine below.
- Views: `dom_launch_list_views` passes through `dom_ui_list_views` so
  front-ends can enumerate `dom_view_desc` entries.
- Process: `dom_launch_run_instance(ctx, inst_id)` spawns/attaches via
  `dsys_process_spawn`.

## State machine
- States: `startup`, `main`, `instance_manager`, `package_manager`,
  `settings`, `running_instance`.
- Default state after `dom_launch_create` is `main`; the preferred view is
  `view_instances` when available (falls back to the first registered view).
- `DOM_LAUNCH_ACTION_QUIT` marks the context as shutting down (state resets to
  `startup`); front-ends decide when to exit their loop.

## Actions
- `LIST_INSTANCES`: switch to `instance_manager`, focus `view_instances`.
- `CREATE_INSTANCE`: builds a `dom_instance_info` with default name (or
  `param_str`) and attaches the first available product/content package, then
  calls `dom_inst_create`; sets `current_instance` on success.
- `EDIT_INSTANCE`: sets `current_instance = param_u32`, state
  `instance_manager`.
- `DELETE_INSTANCE`: calls `dom_inst_delete(param_u32)` and clears
  `current_instance` if it was deleted.
- `LAUNCH_INSTANCE`: calls `dom_launch_run_instance`; on success moves to
  `running_instance` and tracks `current_instance`.
- `LIST_PACKAGES`: switches to `package_manager` and prefers
  `view_packages`/`view_mods`.
- `OPEN_SETTINGS`: moves to `settings` and attempts `view_settings`
  (nullable).
- `VIEW_WORLD`: retargets `current_view_id` to `param_str` or
  `view_world_surface` and keeps the state in `main`.
- `ENABLE_MOD`/`DISABLE_MOD`: records `current_package` (enable/disable wiring
  is deferred to a later revision).
- Custom actions: front-ends can forward string actions via
  `dom_launch_handle_custom_action(ctx, action_id, payload)`; extensions receive
  these through `on_action`.

## Front-end contract
- Create one `dom_core` for the product, then `dom_launch_create` with that
  core and UI mode flag (NONE/CLI/TUI/GUI).
- Poll `dom_launch_get_snapshot` to decide which view/model to render; render
  `current_view_id` using `dom_view`/`dom_table`/`dom_tree`/`dom_canvas`.
- Translate user gestures into `dom_launch_action` calls; the caller already
  knows when `QUIT` is requested.
- Use `dom_launch_list_views` during setup to populate menus/tabs; ordering is
  currently the raw order from `dom_ui_list_views`.

## Running instances
- `dom_launch_run_instance` fetches `dom_instance_info`, guesses an executable
  path from `instance.path` (or the provided `product_id` fallback), builds an
  argv array, and calls `dsys_process_spawn`. IPC/monitoring is deferred; the
  helper simply spawns and frees the process handle.
