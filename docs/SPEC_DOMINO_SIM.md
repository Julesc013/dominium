# Domino Core (filesystem-backed registries)

The Domino core remains deterministic but now mirrors the filesystem. Package
and instance registries are rebuilt on startup by scanning disk and are kept in
sync as commands execute.

## Boot sequence
- `dom_core_create` zeroes state, seeds ids, then:
  1. Scans package roots (official app data + user mods) for directories
     containing `manifest.ini`; loads metadata and assigns incremental package
     ids in sorted path order.
  2. Scans the instances root for `instance.ini`; resolves package references by
     name and assigns incremental instance ids.
  3. Leaves counts and next-id counters ready for commands/queries.

## Commands (`dom_cmd_id`)
- `DOM_CMD_NOP` (0x00000000) – no-op, always succeeds.
- `DOM_CMD_PKG_INSTALL` (0x00010000) – payload `dom_cmd_pkg_install { const char* source_path; }`.
- `DOM_CMD_PKG_UNINSTALL` (0x00010001) – payload `dom_cmd_pkg_uninstall { dom_package_id id; }`.
- `DOM_CMD_INST_CREATE` (0x00020000) – payload `dom_cmd_inst_create { dom_instance_info info; }` (info.struct_size/version must match).
- `DOM_CMD_INST_UPDATE` (0x00020001) – payload `dom_cmd_inst_update { dom_instance_info info; }`.
- `DOM_CMD_INST_DELETE` (0x00020002) – payload `dom_cmd_inst_delete { dom_instance_id id; }`.
- `DOM_CMD_SIM_TICK` (0x00030000) – payload `dom_cmd_sim_tick { dom_instance_id id; uint32_t ticks; }`.

## Queries (`dom_query_id`)
- `DOM_QUERY_CORE_INFO` (0x00000000) – out: `dom_query_core_info_out { struct_size, struct_version, api_version, package_count, instance_count; }`.
- `DOM_QUERY_PKG_LIST` (0x00010000) – out: `dom_query_pkg_list_out { dom_package_info* items; uint32_t max_items; uint32_t count; }`.
- `DOM_QUERY_PKG_INFO` (0x00010001) – in: `dom_query_pkg_info_in { dom_package_id id; }`, out: `dom_query_pkg_info_out { dom_package_id id; dom_package_info info; }`.
- `DOM_QUERY_INST_LIST` (0x00020000) – out: `dom_query_inst_list_out { dom_instance_info* items; uint32_t max_items; uint32_t count; }`.
- `DOM_QUERY_INST_INFO` (0x00020001) – in: `dom_query_inst_info_in { dom_instance_id id; }`, out: `dom_query_inst_info_out { dom_instance_id id; dom_instance_info info; }`.
- `DOM_QUERY_SIM_STATE` (0x00030000) – in: `dom_query_sim_state_in { dom_instance_id id; }`, out: `dom_query_sim_state_out { dom_instance_id id; dom_sim_state state; }`.

## Events
`dom_event_kind`:
- `DOM_EVT_PKG_INSTALLED`
- `DOM_EVT_PKG_UNINSTALLED`
- `DOM_EVT_INST_CREATED`
- `DOM_EVT_INST_UPDATED`
- `DOM_EVT_INST_DELETED`
- `DOM_EVT_SIM_TICKED`

`dom_event` carries `struct_size`, `struct_version`, `kind`, and a union with either `pkg_id` or `inst_id`. Subscribe/unsubscribe with `dom_event_subscribe`/`dom_event_unsubscribe`. Events fire after successful commands and when `dom_sim_tick` advances an instance.

# Behaviour
- Packages: installed via `dom_pkg_install`, assigned incremental ids starting at
  1, metadata stored in `dom_package_info` (struct_size/version = 1) and written
  to disk as `manifest.ini`. Uninstall removes the entry, deletes mod content
  under user data, and keeps official content intact.
- Instances: created with incremental ids, store `dom_instance_info`
  (struct_size/version = 1) and persist to `instance.ini` under the instance
  directory. Update rewrites the descriptor; delete removes both registry entry
  and directory tree.
- Simulation: each instance keeps a `dom_sim_state` (struct_size/version = 1).
  `dom_sim_state {struct_size, struct_version, ticks, sim_time_s, dt_s, ups, paused}`
  is stored per instance inside `dom_core`. `dom_sim_tick(core, inst, n)` looks
  up/creates a sim state (ups defaults to 60 -> dt_s = 1/ups), bails out if
  paused, then loops `n` times calling `dom_game_sim_step(core,{inst,dt_s})`,
  incrementing ticks/time, and finally publishes a single `DOM_EVT_SIM_TICKED`
  for the batch. `dom_sim_get_state` copies the stored state or returns a
  zeroed/defaulted struct when the instance has no sim state yet.
- Dominium handoff: `dom_game_sim_step` is the single hook into the Dominium
  rules surface; it runs a fixed subsystem pipeline (`dom_world_sim_step`,
  `dom_constructions_sim_step`, `dom_actors_sim_step`, then stubbed networks
  and environment/economy).
- Core counts: `dom_query_core_info_out` reports current package/instance counts and api_version from `dom_core_desc`.

## UI stubs
- Canvas: `dom_canvas_build(core, inst, canvas_id, dom_gfx_buffer*)` delegates to
  Dominium builders per instance: `world_surface` (10x10 grid), `world_orbit`
  (orbit rings + marker), `construction_exterior` (outline), and
  `construction_interior` (room grid). Unknown ids return an empty buffer.
- Models/views: a default table model (`instances_table`) and view exist but report no rows yet.

## Notes
- Language: C89 only.
- Everything remains in-memory and deterministic; persistence and real gameplay will be layered on later.
