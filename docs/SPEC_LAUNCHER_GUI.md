# Launcher GUI

The GUI launcher is a minimal immediate-mode front-end built on Domino platform
(`dsys_*`) and renderer (`dgfx_*`). It drives the launcher core (`dom_launch_*`)
and Domino view/canvas models without calling OS APIs directly.

## Layout
- Window: 1280x720 windowed by default (via `dsys_window_create`).
- Tabs (top): Instances, Packages, Mods, World. Each tab maps to a Domino view
  id (`view_instances`, `view_packages`, `view_mods`, `view_world_surface`).
- Content: shows the selected view:
  - Table views (instances/packages/mods) rendered with simple rect/text
    placeholders using `dom_table_get_meta`/`dom_table_get_cell`.
  - World tab: builds a canvas via `dom_canvas_build(core, current_inst,
    "world_surface", &buf)` and feeds the buffer to `dgfx_execute`.
- Status bar (bottom): shows key hints (`F1-F4` tabs, `F5` launch, `ESC` quit)
  and lightweight status text.

## Event loop
- Initialize: `dsys_init` → `dom_core_create` → window + dgfx → `dom_launch_create`
  with `ui_mode = DOM_UI_MODE_GUI`.
- Main loop:
  - Poll `dsys_poll_event` for window close, resize (`dgfx_resize`), and key
    presses (F1-F5, ESC).
  - Fetch `dom_launch_snapshot` to know the current view/instance.
  - Build a frame command buffer through the shared dgfx canvas
    (`dgfx_get_frame_canvas`), draw background, tab bar, content, and status.
  - Submit with `dgfx_begin_frame` → `dgfx_execute` → `dgfx_end_frame`.

## Tab/actions
- F1 → Instances, F2 → Packages, F3 → Mods, F4 → World, F5 → launch selected
  instance, ESC → quit.
- Tab clicks can map to `dom_launch_handle_action` or direct `current_view_id`
  updates; this skeleton wires key shortcuts only, with room for pointer
  handling later.

## Notes
- The GUI uses the dgfx IR only; no external UI toolkit.
- Backends may be swapped by changing `dgfx_desc.backend` (soft, gl2, dx9, etc.).
- This is a skeleton intended to validate the ABIs; styling, text rendering,
  and richer widgets are future work.
- Launch policy is controlled by `launcher_launch_behavior = minimize|close|stay`
  (applied after spawning the game).
- Game spawns set `DOMINIUM_RUN_ROOT` and pass `--handshake=handshake.tlv`
  relative to that run root; `DOMINIUM_HOME` is set when available.
