# Linux Adapter (Plan S-6)

## Overview

The Linux adapter is a thin wrapper around Setup Core intended for:

- portable tarball installs
- `.deb` and `.rpm` packages (package manager owns files)

Linux TUI/CLI frontends must mirror MSI semantics and the canonical UX contract.

Code:

- Adapter entrypoint: `source/dominium/setup/adapters/linux/dominium_setup_adapter_linux.c`

Binary:

- `dominium-setup-linux`

## Commands and parameters

Supported commands:

- `install --plan <file> [--dry-run] [--deterministic] [--log <file>]`
- `uninstall --state <file> [--dry-run] [--deterministic] [--log <file>]`
- `platform-register --state <file> [--deterministic] [--log <file>]`
- `platform-unregister --state <file> [--deterministic] [--log <file>]`

The adapter executes plan/state operations only; invocation payloads are produced by the
frontend or packaging layer and passed to `dominium-setup` for plan creation.

## FHS mapping (recommended)

Package-manager installs should respect FHS:

- binaries: `/usr/bin/` (wrapper) or `/opt/dominium/<version>/bin/`
- shared data: `/usr/share/dominium/`
- per-user state: `~/.local/share/dominium/`
- caches: `~/.cache/dominium/`

Setup Core still computes canonical install roots; the packaging layer should pass the chosen roots deterministically.

## Platform registrations

The Linux adapter implements `dsu_platform_iface` with native filesystem
registrations:

- `.desktop` entries under `~/.local/share/applications/` (user) or
  `/usr/share/applications/` (system)
- MIME XML definitions under `~/.local/share/mime/packages/` or
  `/usr/share/mime/packages/` for file associations and URL handlers

`REGISTER_UNINSTALL_ENTRY` and `DECLARE_CAPABILITY` are no-op success for now.

## Packaging forms (design)

Portable tarball:

- `dominium-setup-linux` + Setup Core payloads
- deterministic layout under a single install root

Debian (`.deb`) / RPM (`.rpm`):

- package scripts should only call Setup Core with invocations (no business logic)
- use `dominium-setup-linux platform-register/unregister` for desktop entries
- ownership belongs to the package manager; avoid overwriting distro-owned files

## Failure modes

- Missing required parameters (`--plan`/`--state`) → `DSU_STATUS_INVALID_ARGS`
- Core failures propagate directly via `dsu_status_t`

## Uninstall behavior

Recommended uninstall flow:

1. `dominium-setup-linux platform-unregister --state <statefile>`
2. `dominium-setup-linux uninstall --state <statefile>`

