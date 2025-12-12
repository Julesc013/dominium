# DVIEW and DUI – view composition and UI IR

## DVIEW (engine-level views)
- **Descriptors:** `d_view_desc` bundles `id`, flags, camera (`d_view_camera`), viewport (`vp_x/y/w/h` in pixel `q16_16` units), layer mask, and optional params TLV.
- **Registry:** `d_view_create` copies a descriptor into a small registry and returns a new `d_view_id`; `d_view_get` returns a mutable descriptor; `d_view_destroy` removes a view.
- **Rendering:** `d_view_render(world, view, frame)` resets the target `dgfx_cmd_buffer`, emits CLEAR, SET_VIEWPORT, and SET_CAMERA IR (identity matrices), then calls stubs `dview_render_world`/`dview_render_ui` for future world/UI rendering. No backend/platform calls are made—only dgfx IR is produced.
- **Viewport:** Stored as fixed-point pixels; callers supply the final viewport size when updating the descriptor.

## DUI (UI widget tree on dgfx)
- **Widgets:** `dui_widget` tree with kinds ROOT, PANEL, LABEL, BUTTON, LIST, each carrying `layout_rect`, computed `final_rect`, flags (`VISIBLE` etc.), text pointer, and an optional `on_click` handler placeholder.
- **Context:** `dui_context` owns the root widget; `dui_init_context` creates ROOT with default visible flags; `dui_shutdown_context` frees the tree.
- **Hierarchy:** `dui_widget_create` allocates a widget with a unique id; `dui_widget_add_child`/`dui_widget_remove_from_parent` manage the tree; `dui_widget_destroy` removes and frees a subtree (root is preserved).
- **Layout:** `dui_layout` stacks visible children of ROOT/PANEL vertically within the parent `final_rect`, defaulting heights to an even split when not specified. Leaves use their `layout_rect` offsets relative to the parent for the final rect.
- **Rendering:** `dui_render(ctx, frame)` traverses depth-first and emits dgfx sprites/text into `frame->cmd_buffer`:
  - ROOT/PANEL/BUTTON/LIST draw filled rects via `DGFX_CMD_DRAW_SPRITES`.
  - LABEL/BUTTON draw text via `DGFX_CMD_DRAW_TEXT`.
  - Colors are simple defaults; all rendering is through dgfx IR only.
- **Integration:** DUI renders into the same `d_view_frame` used by DVIEW; higher layers choose when to call `dui_layout`/`dui_render` after preparing the view’s command buffer.

## Launcher UI
- Implemented in `dom_launcher_ui` on top of DUI: panels for instances, products, mode selection, and a Launch button.
- State (selected instance/product/mode) is held inside `DomLauncherApp`; callbacks only set indices or call `launch_product`.
- Runs against the same DVIEW/dgfx path as the game UI, keeping determinism and backend independence. GUI/TUI are both served via this path for now.
