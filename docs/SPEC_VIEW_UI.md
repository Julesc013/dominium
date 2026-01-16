--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# DVIEW and DUI – minimal GUI slice

## IR and path
- **dgfx IR (minimal):** `d_gfx_cmd` opcodes CLEAR, SET_VIEWPORT, SET_CAMERA, DRAW_RECT, DRAW_TEXT. Command buffers are arrays of these commands, submitted to a backend (soft in this slice) then presented via `d_system_present_framebuffer`.
- **Pipeline:** Dominium Game/Launcher → `d_view_render` emits CLEAR/VIEWPORT/CAMERA → `dui_render` appends rect/text → `d_gfx_submit` → soft backend rasterises → `d_system_present_framebuffer` blits to the OS window.

## DVIEW (engine-level views)
- **Descriptors:** `d_view_desc` holds `id`, flags, `d_view_camera`, normalized viewport (`vp_x/y/w/h` in `q16_16`, 0..1), and layer mask.
- **Registry:** `d_view_create` copies a descriptor into a small registry and returns a `d_view_id`; `d_view_get` returns a mutable descriptor; `d_view_destroy` removes a view.
- **Rendering:** `d_view_render(world, view, frame)` clears, maps the normalized viewport to pixels (default 800×600 if the backend size is unknown), emits camera, then stubs world rendering. No backend/platform calls are made here—only dgfx IR is produced.

## DUI (UI widget tree on dgfx)
- **Widgets:** Kinds ROOT, PANEL, LABEL, BUTTON. Each keeps `layout_rect`, computed `final_rect`, flags, text pointer, and optional `on_click`.
- **Context:** `dui_context` owns the root widget; `dui_init_context` builds ROOT; `dui_shutdown_context` frees the tree.
- **Hierarchy:** `dui_widget_create` allocates; `dui_widget_add_child`/`dui_widget_remove_from_parent` manage the tree; `dui_widget_destroy` frees a subtree (root preserved).
- **Layout:** `dui_layout` stacks visible children of ROOT/PANEL vertically with a small margin/spacing and a default height; children may override via `layout_rect`.
- **Rendering:** `dui_render(ctx, frame)` traverses depth-first and emits DRAW_RECT/DRAW_TEXT through `frame->cmd_buffer`. Colors are simple placeholders; all drawing flows through dgfx IR only.

## Launcher/Game UI snippets
- Game UI (`dom_game_ui_build_root`): root panel with a label "Dominium Game -- GUI Smoke Test".
- Launcher UI (`dom_launcher_ui_build_root`): two labels, "Dominium Launcher" and a summary of discovered products/instances. Both use the same DVIEW+DUI+soft path as the game.
