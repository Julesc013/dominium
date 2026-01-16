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
# Launcher / Tools Protocol

The launcher and tooling sit on top of the Domino core; they never reach into
internal structs. Everything is discovered through the view/model APIs exposed
in public headers.

## Discovering views
- Call `dom_ui_list_views(core, dom_view_desc* out, uint32_t max_out)` to fetch
  the current view list. `dom_view_desc` carries `{id, title, kind, model_id}`
  with `kind` drawn from `DOM_VIEW_KIND_TABLE | TREE | FORM | CANVAS`.
- Default views registered by `dom_core_create`:
  - `view_instances` → TABLE → `instances_table`
  - `view_packages` → TABLE → `packages_table`
  - `view_mods` → TABLE → `mods_table`
  - `view_packages_tree` → TREE → `packages_tree`
  - `view_world_surface` → CANVAS → `world_surface`
  - `view_world_orbit` → CANVAS → `world_orbit`
- Future launcher extensions (`launcher_ext`) will be able to register
  additional views; discovery always flows through `dom_ui_list_views`.

## TABLE views
- Each table is a read-only model accessed through:
  - `dom_table_get_meta(core, table_id, dom_table_meta*)` → row/column counts
    and `col_ids[]`.
  - `dom_table_get_cell(core, table_id, row, col, char* buf, size_t buf_size)`
    → materializes a single cell as a string (rows/cols are zero-based).
- Built-in tables:
  - `packages_table`: cols `id,name,version,kind,path`; rows mirror the package
    registry.
  - `instances_table`: cols `id,name,path,flags,pkg_count,last_played`
    (`last_played` is currently a placeholder).
  - `mods_table`: same shape as `packages_table` filtered to
    `DOM_PKG_KIND_MOD`/`DOM_PKG_KIND_CONTENT`.
- Launchers should render column headers from `col_ids` and cache nothing else;
  mutations happen via commands, not via the model API.

## TREE views
- Accessed via `dom_tree_get_root/get_node/get_child`. Nodes expose
  `{parent,label,child_count}` and are computed on demand.
- `packages_tree` layout:
  - Root label `"Packages"`.
  - Children: one node per package kind (Unknown, Mods, Content, Products,
    Tools, Packs).
  - Leaves: package nodes under their kind parent, label = package name.
- Node ids are synthetic and must be treated as opaque by the launcher.

## CANVAS views
- Use `dom_canvas_build(core, dom_instance_id inst, const char* canvas_id,
  dom_gfx_buffer* out)` with `canvas_id = model_id` from the view descriptor.
- Built-in canvases: `world_surface`, `world_orbit`,
  `construction_exterior`, `construction_interior`. Unknown ids return an empty
  buffer. Instance id is passed through from the caller (0 is valid for
  instance-agnostic canvases).
