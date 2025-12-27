# Linux Installer Suite

## Overview

Linux installers are thin frontends over Setup Core. They only collect user
choices, emit `dsu_invocation`, and call `dominium-setup` for plan/apply.

Frontends:

- CLI: `dominium-setup` (authoritative reference)
- TUI: `dominium-setup-tui`
- GUI: `dominium-setup-gui` (launches the TUI in a terminal when available)

All frontends emit deterministic invocation payloads and log digests for parity
with MSI/EXE installers.

## Supported operations

- detect
- install / upgrade
- repair / verify
- uninstall

## Scope mapping

- `portable` -> `<artifact_root>/install/portable` (default for tarball)
- `user` -> `~/.local/share/dominium`
- `system` -> `/opt/dominium`

The actual root is taken from `product.dsumanifest` unless overridden by
`--install-root`.

## CLI examples (reference)

Export invocation and apply:

```
dominium-setup export-invocation --manifest setup/manifests/product.dsumanifest \
  --op install --scope system --platform linux-x64 --install-root "/opt/dominium" \
  --ui-mode cli --frontend-id cli-linux --out /tmp/dominium.dsuinv --deterministic 1

dominium-setup plan --manifest setup/manifests/product.dsumanifest \
  --invocation /tmp/dominium.dsuinv --out /tmp/dominium.dsuplan --deterministic 1

dominium-setup apply --plan /tmp/dominium.dsuplan --deterministic 1
```

Silent repair:

```
dominium-setup export-invocation --manifest setup/manifests/product.dsumanifest \
  --op repair --scope system --platform linux-x64 \
  --install-root "/opt/dominium" --ui-mode cli --frontend-id cli-linux \
  --out /tmp/dominium_repair.dsuinv --deterministic 1
dominium-setup plan --manifest setup/manifests/product.dsumanifest \
  --invocation /tmp/dominium_repair.dsuinv --out /tmp/dominium_repair.dsuplan --deterministic 1
dominium-setup apply --plan /tmp/dominium_repair.dsuplan --deterministic 1
```

## TUI usage

Interactive:

```
dominium-setup-tui
```

Non-interactive (headless):

```
dominium-setup-tui --non-interactive --manifest setup/manifests/product.dsumanifest \
  --op install --scope portable --install-root "/opt/dominium" \
  --export-invocation --out /tmp/dominium.dsuinv
```

The TUI prints the equivalent CLI command for reproducibility.

## GUI usage

```
dominium-setup-gui
```

The GUI is a minimal wrapper that launches the TUI in a terminal emulator when
available. It has no external GUI toolkit dependencies.

## Desktop integration

Platform registrations are executed by `dominium-setup-linux` using intents
stored in the installed state:

- `.desktop` entries
- MIME file associations
- URL handlers

Frontends call `dominium-setup-linux platform-register` after successful apply,
and `platform-unregister` before uninstall.

## Parity guarantees

- Invocation digests emitted by the Linux TUI/GUI match CLI inputs.
- Plan digests match across CLI and TUI for the same invocation payload.
- Offline-first: no network access is required for install/repair/uninstall.
