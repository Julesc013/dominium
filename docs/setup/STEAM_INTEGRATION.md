# Steam Integration (Plan S-6)

## Overview

Steam distribution must not bypass Setup Core. Steam lifecycle events are mapped into Setup Core operations and state transitions.

Code:

- Adapter entrypoint: `source/dominium/setup/adapters/steam/dominium_setup_adapter_steam.c`

Binary:

- `dominium-setup-steam`

## Depot layout (design)

Recommended SteamPipe depot contents:

- `dominium-setup-steam` (or platform-specific launcher that invokes it)
- Setup Core payloads:
  - manifests
  - plan/state schemas
  - archives/blobs required by the transaction engine
- game/launcher binaries and content

Steam itself is responsible for downloading depots; Setup Core remains responsible for applying plans and writing installed state.

## Lifecycle mapping

| Steam event | Adapter action | Setup Core call(s) |
|------------|----------------|--------------------|
| install    | apply plan     | `dsu_txn_apply_plan` |
| update     | apply plan     | `dsu_txn_apply_plan` (upgrade plan) |
| verify     | verify state   | `dsu_txn_verify_state` (future) |
| uninstall  | uninstall      | `dsu_txn_uninstall_state` |

## Parameters

The Steam adapter supports:

- `install --plan <file> [--dry-run] [--deterministic] [--log <file>]`
- `uninstall --state <file> [--dry-run] [--deterministic] [--log <file>]`

Platform registrations (file associations, URL handlers, uninstall entries) should be handled by the OS adapter, not by Steam.

## Failure modes

- Missing required parameters → `DSU_STATUS_INVALID_ARGS`
- Core failures propagate directly via `dsu_status_t`

## Uninstall behavior

Recommended uninstall flow in Steam context:

1. (optional) OS adapter `platform-unregister` using the installed state
2. `dominium-setup-steam uninstall --state <statefile>`

