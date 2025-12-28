# macOS Adapter (Plan S-6)

## Overview

The macOS adapter is a thin wrapper around Setup Core for `.pkg`/`.dmg` distribution flows.
macOS GUI frontends must follow the canonical UX contract (expert UI allowed).

Code:

- Adapter entrypoint: `source/dominium/setup/adapters/macos/dominium_setup_adapter_macos.c`

Binary:

- `dominium-setup-macos`

## Commands and parameters

Supported commands:

- `install --plan <file> [--dry-run] [--deterministic] [--log <file>]`
- `uninstall --state <file> [--dry-run] [--deterministic] [--log <file>]`
- `platform-register --state <file> [--deterministic] [--log <file>]`
- `platform-unregister --state <file> [--deterministic] [--log <file>]`

The adapter executes plan/state operations only; invocation payloads are produced by the
frontend or packaging layer and passed to `dominium-setup` for plan creation.

## Platform registrations

The current macOS adapter implements `dsu_platform_iface` with a minimal native
app bundle registration:

- creates a `.app` bundle in the Applications directory (system/user/portable)
- writes a basic `Info.plist` and a wrapper shell script that launches the
  installed executable from the install root
- `platform-register` / `platform-unregister` are idempotent

File associations and URL handlers are recorded as intents and treated as
best-effort placeholders; they currently ensure the app bundle exists and are
documented for future LaunchServices integration.

## Installer layout (design)

Recommended `.pkg` payload roots:

- `/Applications/Dominium.app` (app bundle)
- state and caches under the install root selected by Setup Core

Recommended `.dmg` layout:

- `Dominium.app`
- alias/link to `/Applications`
- optional `README` / `LICENSE`

## Elevation

System scope placement under `/Applications` and other privileged locations should be handled by the native `.pkg` flow.
`plat_request_elevation` is a stub returning `DSU_STATUS_INVALID_REQUEST`.

## Failure modes

- Missing required parameters (`--plan`/`--state`) → `DSU_STATUS_INVALID_ARGS`
- Core failures propagate directly via `dsu_status_t`

## Uninstall behavior

Recommended uninstall flow:

1. `dominium-setup-macos platform-unregister --state <statefile>` (currently no-op)
2. `dominium-setup-macos uninstall --state <statefile>`

