# Platform Adapters (Plan S-6)

Setup Core is deterministic and OS-agnostic. **Platform adapters** are thin, replaceable shells that:

- collect user/installer parameters (paths, scope, component selection) by emitting `dsu_invocation`
- handle privilege elevation and UI flow
- invoke Setup Core exclusively through the stable C ABI
- execute declarative platform registrations by implementing `dsu_platform_iface`

Adapters must not duplicate Setup Core business logic or add heuristics/retries.

## Directory layout

- Setup Core (OS-agnostic): `source/dominium/setup/core/`
- Public platform adapter ABI: `include/dsu/dsu_platform_iface.h`
- Platform adapter implementations: `source/dominium/setup/adapters/`
  - Windows: `source/dominium/setup/adapters/windows/`
  - macOS: `source/dominium/setup/adapters/macos/`
  - Linux: `source/dominium/setup/adapters/linux/`
  - Steam: `source/dominium/setup/adapters/steam/`

## Stable C ABI surface used by adapters

Typical adapter flow uses:

- Context + deterministic policy:
  - `dsu_config_init`, `dsu_ctx_create`, `dsu_ctx_set_platform_iface`
- Plan/state IO:
  - `dsu_plan_read_file`, `dsu_state_load_file`
- Transaction operations:
  - `dsu_txn_apply_plan`, `dsu_txn_uninstall_state`
- Declarative platform registrations:
  - `dsu_platform_register_from_state`, `dsu_platform_unregister_from_state`

## Common lifecycle (recommended)

The native installer ecosystem controls the high-level lifecycle; adapters only translate it into core calls:

1. **Install/Upgrade/Repair**
   - emit a `dsu_invocation` (frontend)
   - build a `.dsuplan` from the invocation (Setup Core)
   - apply it via `dsu_txn_apply_plan`
2. **Register platform integrations**
   - load installed state (`.dsustate`)
   - call `dsu_platform_register_from_state` (adapter must provide `dsu_platform_iface`)
3. **Unregister + Uninstall**
   - load installed state (`.dsustate`)
   - call `dsu_platform_unregister_from_state`
   - call `dsu_txn_uninstall_state`

## Determinism and safety

- **Deterministic mode**: adapters pass `DSU_CONFIG_FLAG_DETERMINISTIC` when requested; they do not “fix up” arguments or inject timestamps.
- **Canonical parameter ordering**: where adapters accept lists (components, exclusions), they should sort canonically before calling core.
- **Audit log**: adapters write or forward logs into the Setup Core audit log and persist with `dsu_log_write_file`.
- **No adapter-level retries**: failures propagate to the caller deterministically via `dsu_status_t`.

## Platform interface contract (`dsu_platform_iface`)

Core emits **intents** and calls the interface; adapters execute them:

- `plat_register_app_entry`
- `plat_register_file_assoc`
- `plat_register_url_handler`
- `plat_register_uninstall_entry`
- `plat_remove_registrations`

The unregister path is always driven by the installed state: `dsu_platform_unregister_from_state` calls `plat_remove_registrations` with the decoded intents.

## CLI surface (adapter-backed)

- Register platform intents:
  - `dominium-setup platform-register --state <install_root>/.dsu/installed_state.dsustate --deterministic 1`
- Unregister platform intents:
  - `dominium-setup platform-unregister --state <install_root>/.dsu/installed_state.dsustate --deterministic 1`

Exit codes follow `docs/setup/CLI_REFERENCE.md`.

## Invariants and prohibitions

- Adapters must treat intent lists as authoritative and deterministic; no reordering.
- Adapters must not invent or mutate intents; they only execute what the installed state encodes.

## See also

- `docs/setup/WINDOWS_ADAPTER.md`
- `docs/setup/MACOS_ADAPTER.md`
- `docs/setup/LINUX_ADAPTER.md`
- `docs/setup/STEAM_INTEGRATION.md`
