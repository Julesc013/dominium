# Minecraft-Style Setup UI Smoke Test

This document describes the structure-only Minecraft-style setup wizard layout
used for UI validation. No theming, custom colors, or non-native controls are
part of this pass.

## What "Minecraft-style" Means Here

- Header/title at the top, footer navigation at the bottom.
- Body uses tabs as wizard pages (Welcome, Path, Components, Progress, Finish).
- Native Win32 controls only (static text, edit, buttons, list, progress).
- Navigation buttons exist for Back/Next/Install/Finish/Cancel.

## Build Commands

```
cmake --build build\msvc-debug --config Debug --target dominium-ui-editor
cmake --build build\msvc-debug --config Debug --target dominium-setup
```

## Regenerate UI Docs

Preferred path (CMake target):

```
cmake --build build\msvc-debug --config Debug --target ui_regen_setup
```

Direct CLI path (equivalent):

```
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-apply tools\setup\ui\doc\setup_ui_doc.tlv --script tools\setup\ui\scripts\minecraft_setup_v1.ops.json --out tools\setup\ui\doc\setup_ui_doc.tlv --in-new
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-format tools\setup\ui\doc\setup_ui_doc.tlv
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-codegen --in tools\setup\ui\doc\setup_ui_doc.tlv --out tools\setup\ui\gen --registry tools\setup\ui\registry\setup_actions_registry.json --docname setup_ui
```

## Smoke Checklist

- Header visible with title text.
- Footer buttons present: Back, Next, Install, Finish, Cancel.
- Body has 5 pages (Welcome, Install Location, Components, Progress, Finish).
- Install Location page has path edit and Browse button.
- Progress page shows progress bar and log box.
- Finish page shows summary and optional launch checkbox.
- No crashes; action stubs compile cleanly.
