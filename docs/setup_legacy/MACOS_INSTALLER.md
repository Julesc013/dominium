# macOS Installer Suite

## Overview

macOS installers are thin frontends over Setup Core. They collect user
choices, emit `dsu_invocation`, and call `dominium-setup` for plan/apply.

Frontends:

- CLI: `dominium-setup` (authoritative reference)
- TUI: `dominium-setup-tui`
- GUI: `dominium-setup-gui` (Cocoa app, also supports `--export-invocation`)

All frontends emit deterministic invocation payloads and log digests for parity
with MSI/EXE installers.

## Supported operations

- detect
- install / upgrade
- repair / verify
- uninstall

## Scope mapping

Install roots come from `product.dsumanifest` unless overridden:

- `portable` -> `install/portable`
- `user` -> `~/Library/Application Support/Dominium`
- `system` -> `/Applications/Dominium`

## CLI examples (reference)

Export invocation and apply:

```
dominium-setup export-invocation --manifest setup/manifests/product.dsumanifest \
  --op install --scope system --platform macos-x64 --install-root "/Applications/Dominium" \
  --ui-mode gui --frontend-id gui-macos --out /tmp/dominium.dsuinv --deterministic 1

dominium-setup plan --manifest setup/manifests/product.dsumanifest \
  --invocation /tmp/dominium.dsuinv --out /tmp/dominium.dsuplan --deterministic 1

dominium-setup apply --plan /tmp/dominium.dsuplan --deterministic 1
```

Silent uninstall:

```
dominium-setup export-invocation --manifest setup/manifests/product.dsumanifest \
  --op uninstall --scope system --platform macos-x64 \
  --install-root "/Applications/Dominium" --ui-mode cli --frontend-id cli-macos \
  --out /tmp/dominium_uninstall.dsuinv --deterministic 1
dominium-setup plan --manifest setup/manifests/product.dsumanifest \
  --invocation /tmp/dominium_uninstall.dsuinv --out /tmp/dominium_uninstall.dsuplan --deterministic 1
dominium-setup apply --plan /tmp/dominium_uninstall.dsuplan --deterministic 1
```

## TUI usage

Interactive:

```
dominium-setup-tui
```

Non-interactive:

```
dominium-setup-tui --non-interactive --manifest setup/manifests/product.dsumanifest \
  --op install --scope portable --install-root "/Applications/Dominium" \
  --export-invocation --out /tmp/dominium.dsuinv
```

The TUI prints the equivalent CLI command for reproducibility.

## GUI usage

Launch from Terminal:

```
dominium-setup-gui
```

Headless invocation export (used for parity tests):

```
dominium-setup-gui --manifest setup/manifests/product.dsumanifest \
  --op install --scope system --platform macos-x64 \
  --install-root "/Applications/Dominium" \
  --export-invocation --out /tmp/dominium_gui.dsuinv --deterministic 1 --non-interactive
```

## Desktop integration

Platform registrations are executed by `dominium-setup-macos` using intents
stored in the installed state:

- app bundle registration (Applications folder)
- file associations (best-effort placeholder)
- URL handlers (best-effort placeholder)

Frontends call `dominium-setup-macos platform-register` after successful apply,
and `platform-unregister` before uninstall.

## Parity guarantees

- Invocation digests emitted by the macOS GUI match CLI inputs.
- Plan digests match across CLI and GUI for the same invocation payload.
- Offline-first: no network access is required for install/repair/uninstall.
