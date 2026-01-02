# Windows Adapter (Plan S-6)

## Overview

The Windows adapter is a thin wrapper around Setup Core that:

- parses MSI-style flags (`/quiet`, `/passive`)
- executes plan/state operations produced by Setup Core
- executes declarative platform registrations by implementing `dsu_platform_iface` using Windows Registry writes

MSI is the canonical Windows installer model; EXE frontends must be parity clones
that emit identical invocation payloads for identical inputs.

Code:

- Adapter entrypoint: `source/dominium/setup/adapters/windows/dominium_setup_adapter_windows.c`
- Platform iface impl: `source/dominium/setup/adapters/windows/dsu_windows_platform_iface.c`

Binary:

- `dominium-setup-win`

## Commands and parameters

Supported commands:

- `install --plan <file> [--dry-run] [--deterministic] [--log <file>] [/quiet|/passive]`
- `uninstall --state <file> [--dry-run] [--deterministic] [--log <file>] [/quiet|/passive]`
- `platform-register --state <file> [--deterministic] [--log <file>] [/quiet|/passive]`
- `platform-unregister --state <file> [--deterministic] [--log <file>] [/quiet|/passive]`

Notes:

- `/quiet` suppresses adapter stdout/stderr (except fatal usage).
- `/passive` is treated as “noisy but non-interactive”.
- `--deterministic` sets `DSU_CONFIG_FLAG_DETERMINISTIC` for stable outputs.
- `--log` writes the Setup Core audit log via `dsu_log_write_file`.
- The adapter does not build invocations; MSI/EXE frontends generate `dsu_invocation` and call `dominium-setup` to plan/apply.

## Registry mapping (current minimal implementation)

Scope selection:

- `portable` / `user` scope → `HKCU`
- `system` scope → `HKLM` (requires elevation; failures surface as `DSU_STATUS_IO_ERROR`)

Keys written:

- App entry (`DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY`)
  - `Software\Microsoft\Windows\CurrentVersion\App Paths\<exe>` (default value = absolute exe path)
- File association (`DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC`)
  - `Software\Classes\<extension>` (default value = `<app_id><extension>`)
  - `Software\Classes\<app_id><extension>\shell\open\command` (default value = `"exe" args`)
- URL handler (`DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER`)
  - `Software\Classes\<protocol>` (default value = `display_name`)
  - `Software\Classes\<protocol>\URL Protocol` = `""`
  - `Software\Classes\<protocol>\shell\open\command` (default value = `"exe" args`)
- Uninstall entry (`DSU_PLATFORM_INTENT_REGISTER_UNINSTALL_ENTRY`)
  - `Software\Microsoft\Windows\CurrentVersion\Uninstall\<app_id>`
    - `DisplayName`, `DisplayVersion`, `Publisher` (optional), `InstallLocation`
    - `UninstallString`, `QuietUninstallString`

Unregister:

- `platform-unregister` calls `plat_remove_registrations`, which removes the keys implied by the intents in the installed state.

## Elevation

`plat_request_elevation` is currently a stub returning `DSU_STATUS_INVALID_REQUEST`.

For system-scope installs, integrate elevation at the installer layer (MSI / bootstrapper) before invoking Setup Core.

## MSI integration (current)

The MSI WiX sources live under:

- `source/dominium/setup/installers/windows/msi/wix/`

The MSI maps UI selections to `dsu_invocation` and invokes:

- `dominium-setup apply --invocation <payload>`

Platform registrations are executed by Setup Core via `dsu_platform_iface`.
MSI does not call `dominium-setup-win` directly.

## Failure modes

- Missing required parameters (`--plan`/`--state`) → `DSU_STATUS_INVALID_ARGS`
- Registry write/delete failures (common cause: insufficient privileges for `HKLM`) → `DSU_STATUS_IO_ERROR`

## Uninstall behavior

The recommended Windows uninstall flow is:

1. `dominium-setup-win platform-unregister --state <statefile>`
2. `dominium-setup-win uninstall --state <statefile>`

