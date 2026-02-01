Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Minecraft-Style Launcher UI Smoke Test

This document describes the structure-only Minecraft-style launcher layout used
for UI validation. No theming, custom colors, or non-native controls are part of
this pass.

## What “Minecraft-style” Means Here

- Header/banner at the top, footer/status at the bottom.
- Sidebar navigation on the left with stacked buttons.
- Primary content area uses tabs (Home/News, Instances, Settings).
- Home tab contains a scrollable news list.
- Instances tab uses a left list and right detail panel split.
- Settings tab uses stacked group boxes with native controls.

## Build Commands

```
cmake --build build\msvc-debug --config Debug --target dominium-ui-editor
cmake --build build\msvc-debug --config Debug --target dominium-launcher
```

## Regenerate UI Docs

Preferred path (CMake target):

```
cmake --build build\msvc-debug --config Debug --target ui_regen_launcher
```

Direct CLI path (equivalent):

```
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-apply tools\launcher\ui\doc\launcher_ui_doc.tlv --script tools\launcher\ui\scripts\minecraft_launcher_v1.ops.json --out tools\launcher\ui\doc\launcher_ui_doc.tlv --in-new
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-format tools\launcher\ui\doc\launcher_ui_doc.tlv
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-codegen --in tools\launcher\ui\doc\launcher_ui_doc.tlv --out tools\launcher\ui\gen --registry tools\launcher\ui\registry\launcher_actions_registry.json --docname launcher_ui
```

## Smoke Checklist

- Header visible with title and version text.
- Sidebar buttons present: Play, Instances, Settings, Mods.
- Tabs switch pages (Home/Instances/Settings).
- Home tab scroll panel shows stacked news items.
- Instances tab shows list/detail split.
- Footer status text visible and right build label anchored.
- No crashes; action stubs compile cleanly.