# Domino In-Memory Core (stub)

This document describes the temporary, compile-ready Domino core ABI. Everything here is implemented with simple in-memory structures and will be expanded with real persistence and simulation later on.

## Core handle
- `dom_core` is created from `dom_core_desc { api_version }`.
- Commands: only `DOM_CMD_NOP` is accepted for now.
- Queries: `DOM_QUERY_CORE_INFO` returns `dom_core_info` (api_version, package/instance counts, tick counter).
- The core owns in-memory registries for packages, instances, views, and event subscriptions. No external resources are touched.

## Packages and instances
- Packages use `dom_package_info` with basic metadata and dependency slots. `dom_pkg_install` just registers a new entry with an auto-incremented id and the provided source path string.
- Instances use `dom_instance_info`; creation assigns an id and keeps a list of package ids. Everything lives in memory only; `list/get/update/delete` mutate the registry directly.

## Simulation
- Per-instance `dom_sim_state` lives alongside instances. `dom_sim_tick` adds ticks and advances time using a fixed 1/60s step. `dom_sim_get_state` reports the current state.

## Canvas
- `dom_canvas_build` writes a single `DGFX_CMD_CLEAR` into the supplied buffer when asked for `world_surface` or `preview` canvases. Other canvas ids return an empty buffer. No rendering backends are invoked.

## Models and views
- Table model: `instances_table` exposes three columns (`id`, `name`, `path`) and currently reports zero rows. `dom_table_get_cell` returns false because there is no data yet.
- Tree model: stub root node (id=1) with no children.
- Views: `dom_ui_list_views` returns a default view targeting `instances_table`. Kind/form/canvas slots exist for future expansion.

## Event bus
- `dom_event_subscribe`/`dom_event_unsubscribe` manage an in-memory subscriber list keyed by `dom_event_kind`. `DOM_EVT_NONE` is the only defined kind. An internal publisher exists but no code emits events yet.

## Plugins
- `dom_mod_vtable` and `launcher_ext_vtable` are defined for future plugins, but `dom_mod_load_all` / `launcher_ext_load_all` are stubs that simply succeed without loading anything.

## Notes
- Language: C89 only.
- No filesystem IO, network activity, or platform-specific headers are involved in these stubs.
- These APIs are placeholders to let the launcher and future tools compile and link; expect them to change as real engine logic is added.
