# Read-Only Adapter

The read-only adapter isolates application code from engine/game headers and
centralizes compatibility checks and read-only queries.

## Location
- API: `app/include/dominium/app/readonly_adapter.h`
- Implementation: `app/src/readonly_adapter.c`

## Contract
- `dom_app_ro_open` runs `dom_app_compat_check` and fails on build-info ABI/struct
  mismatches or explicit `--expect-*` constraints.
- `dom_app_ro_last_error` exposes adapter failures (for example: core create failure).
- Schema version `DOM_APP_RO_SCHEMA_VERSION` applies to adapter structs.

## Supported operations
- Core info: package/instance counts (`dom_app_ro_get_core_info`)
- Topology: `packages_tree` (`dom_app_ro_get_tree`)
- Tables: `packages_table`, `instances_table`, `mods_table`
- Simulation state: `dom_app_ro_get_sim_state`

## Unsupported (APR4)
- Snapshots
- Event stream history
- Replay read APIs
- Authority tokens

Unsupported requests must fail loudly with explicit diagnostics.
