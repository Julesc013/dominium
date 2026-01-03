# IDE Live Editing (Preview Hosts)

This document describes IDE-native live preview workflows for Dominium tools
without replacing the canonical DUI pipeline.

## Philosophy

- Canonical source of truth is `ui_doc.tlv` (and its JSON mirror).
- Action bindings are stable keys resolved through the registry.
- IDEs drive preview hosts; native views are never canonical unless exported.
- Automation edits `ops.json` and regenerates the TLV via the canonical pipeline.
- `ui_doc.json` is read-only; treat it as a deterministic mirror.

## Preview Host Overview

Preview hosts live under `tools/ui_preview_host/`:

- Windows: `dominium-ui-preview-host-win32`
- macOS: `dominium-ui-preview-host-macos`
- Linux: `dominium-ui-preview-host-linux`

CLI:

```
--ui <path/to/ui_doc.tlv>
--targets <backend/tier list>
--watch
--log <path>
```

All hosts validate and render from TLV. When the platform backend is missing,
they fall back to the DUI null backend (validation + event logging only).

## Windows (Visual Studio 2026)

1. Configure with the preset:
   `cmake --preset windows-msvc-vs2026`
2. Open the solution generated in `build/windows-msvc-vs2026`.
3. Set `dominium-ui-preview-host-win32` as the startup project.
4. Debug arguments and working directory are preconfigured by CMake:
   `--ui tools/launcher/ui/doc/launcher_ui_doc.tlv --watch`
5. For a full regen + preview loop, build the custom target:
   `ui_preview_launcher_win32` (or `ui_preview_setup_win32`).

Notes:
- The preview targets run:
  `dominium-ui-editor --headless-build-ui --in <doc> --docname <name> --out-root tools/<tool>/ui`
  before launching the host.
- Edit `tools/<tool>/ui/scripts/*.ops.json` and rebuild the preview target.

Optional: Visual Studio External Tools
- Add an External Tool that runs `dominium-ui-preview-host-win32` with the same
  arguments for a one-click live preview.

## macOS (Xcode)

1. Configure with the preset:
   `cmake --preset macos-xcode`
2. Open `build/macos-xcode/DominiumDomino.xcodeproj`.
3. Select `dominium-ui-preview-host-macos` and run.
   CMake provides default scheme args:
   `--ui tools/launcher/ui/doc/launcher_ui_doc.tlv --watch`
4. To enforce regen before running, build the custom target:
   `ui_preview_launcher_macos` (or `ui_preview_setup_macos`).

The macOS preview host uses `kqueue` to watch file changes and hot reload.

## Linux (VS Code, CLion, CLI)

### VS Code

- Configure: `cmake --preset linux-dev`
- Build preview host: `cmake --build --preset linux-dev --target dominium-ui-preview-host-linux`
- Run: `build/linux-dev/dominium-ui-preview-host-linux --ui tools/launcher/ui/doc/launcher_ui_doc.tlv --watch`

The repo includes example VS Code tasks and a launch config under:
- `docs/ui_editor/ide/vscode/tasks.json`
- `docs/ui_editor/ide/vscode/launch.json`
Copy them into `.vscode/` as needed (the repo ignores `.vscode`).

### CLion

- Create a CMake profile that uses the `linux-dev` preset.
- Build and run `ui_preview_launcher_linux` (or run `dominium-ui-preview-host-linux`
  with the `--ui ... --watch` arguments).

### CLI

```
cmake --preset linux-dev
cmake --build --preset linux-dev --target ui_preview_launcher_linux
```

The Linux preview host uses inotify to watch file changes.

## Native Editing Strategy

- Edit `ops.json` and rebuild (`ui_regen_<tool>` or `ui_preview_<tool>_*`).
- Native toolkits are preview surfaces only; exports must go through canonical
  TLV validation and codegen.
- The JSON mirror is not an editable artifact.

## Phase 2 Importers (Stubs)

One-way importers are intentionally deferred; these are the planned hooks:

- Windows: `.rc/.dlg` -> `ui_doc.tlv`
- macOS: `.xib/.storyboard` -> `ui_doc.tlv`
- Linux: GtkBuilder XML -> `ui_doc.tlv`

Proposed contract:

- New CLI entry points on `dominium-ui-editor`:
  `--import-rc`, `--import-xib`, `--import-gtk`.
- Importers must emit canonical TLV and a deterministic report JSON.
- Imported widgets must map to stable action keys; unresolved keys become
  placeholders that fail validation until resolved.

## Troubleshooting

- No hot reload: verify `--watch` and that the UI doc path resolves under
  `tools/<tool>/ui/doc/`.
- Stale codegen: run `ui_regen_<tool>` or `dominium-ui-editor --headless-build-ui`.
- Validation failures: check the preview host log (`--log`) and run
  `dominium-ui-editor --headless-validate` with `--targets`.
- Backend unavailable: the host falls back to the null backend; ensure your
  platform backend is enabled and available.

## Verification Checklist

- Windows: edit `ops.json` -> build/run -> preview host updates without restart.
- macOS: edit `ops.json` -> build/run -> preview host updates without restart.
- Linux: edit `ops.json` -> build/run -> preview host updates without restart.
