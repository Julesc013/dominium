# APR4 Engine/Game Interface Inventory

This inventory captures engine/game public read-only interfaces available to
the application layer. It does not add or modify engine/game behavior.

## Engine (Domino) public interfaces

### Build/version
- `domino/version.h`: `DOMINO_VERSION_*`, `DOMINO_VERSION_STRING`
- `domino/build_info.h`: `dom_build_info_v1_get()`, `dom_build_id()`,
  `dom_git_hash()`, `dom_toolchain_id()`, `dom_sim_schema_id()`
- `domino/compat.h`: compat profiles and `dom_decide_compat()` utilities

### Core/query (read-only capable)
- `domino/core.h`: `dom_core_create()`, `dom_core_query()` with:
  - `DOM_QUERY_CORE_INFO`
  - `DOM_QUERY_PKG_LIST` / `DOM_QUERY_PKG_INFO`
  - `DOM_QUERY_INST_LIST` / `DOM_QUERY_INST_INFO`
  - `DOM_QUERY_SIM_STATE`
- `domino/pkg.h`: `dom_pkg_list()` / `dom_pkg_get()`
- `domino/inst.h`: `dom_inst_list()` / `dom_inst_get()`
- `domino/sim.h`: `dom_sim_get_state()`

### Topology / models
- `domino/model_tree.h` (implemented): `dom_tree_get_root/get_node/get_child`
  - `packages_tree` (package-kind hierarchy)
- `domino/model_table.h` (implemented): `dom_table_get_meta/get_cell`
  - `packages_table`, `instances_table`, `mods_table`
- `domino/view.h` (implemented): `dom_ui_list_views()`

### Events
- `domino/event.h`: `dom_event_subscribe()` / `dom_event_unsubscribe()`
  - No engine event publish sites found in current codebase; treat as
    unsupported for stream summaries until publishers exist.

## Game (Dominium) public interfaces

### Game runtime
- `dominium/game_api.h`: `dom_game_runtime_*` plus `dom_game_runtime_query()`
  - Requires runtime creation and is not used in APR4 read-only adapter.

### Version
- `dom_contracts/version.h`: `dominium_get_*_version_string()` and
  `DOMINIUM_*_VERSION` macros

## Not present / unsupported for APR4
- Snapshot creation/release APIs (no public header found)
- Event stream history APIs (subscription only; no publishers observed)
- Topology beyond `packages_tree` / model tables
- Replay read APIs (no public replay header in engine include)
- Authority token acquisition (no public header found)
- Public serialization hooks for snapshots/replays

These are documented as unsupported and must fail loudly when requested.
