# UI Workflow End-to-End (Headless + GUI)

This document captures the full UI workflow from discovery to build validation.
Use headless commands where possible; legacy import is GUI-only in this phase.

## 1) Discover UI Projects

```
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --scan-ui --out tools\ui_index\ui_index.json
```

## 2) Import Legacy UI (GUI)

Open `dominium-ui-editor` and use:

- `File -> Import Legacy UI...`

This creates `ui_doc.tlv`, `ui_doc.json`, and `import_report.json` without
modifying the legacy TLV.

## 3) Apply ops.json (Headless)

Launcher:

```
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-apply tools\launcher\ui\doc\launcher_ui_doc.tlv --script tools\launcher\ui\scripts\minecraft_launcher_v1.ops.json --out tools\launcher\ui\doc\launcher_ui_doc.tlv --in-new
```

Setup:

```
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-apply tools\setup\ui\doc\setup_ui_doc.tlv --script tools\setup\ui\scripts\minecraft_setup_v1.ops.json --out tools\setup\ui\doc\setup_ui_doc.tlv --in-new
```

## 4) Format / Canonicalize

```
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-format tools\launcher\ui\doc\launcher_ui_doc.tlv
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-format tools\setup\ui\doc\setup_ui_doc.tlv
```

## 5) Codegen

```
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-codegen --in tools\launcher\ui\doc\launcher_ui_doc.tlv --out tools\launcher\ui\gen --registry tools\launcher\ui\registry\launcher_actions_registry.json --docname launcher_ui
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-codegen --in tools\setup\ui\doc\setup_ui_doc.tlv --out tools\setup\ui\gen --registry tools\setup\ui\registry\setup_actions_registry.json --docname setup_ui
```

## 6) Build Targets

```
cmake --build build\msvc-debug --config Debug --target dominium-launcher
cmake --build build\msvc-debug --config Debug --target dominium-setup
```

## 7) Validate Docs (Headless)

```
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-validate tools\launcher\ui\doc\launcher_ui_doc.tlv --targets win32_t1
build\msvc-debug\out\bin\Debug\dominium-ui-editor.exe --headless-validate tools\setup\ui\doc\setup_ui_doc.tlv --targets win32_t1
```

## 8) One-Command Gate

```
cmake --build build\msvc-debug --config Debug --target ui_capability_test
```

## Artifact Policy

- Canonical docs and ops scripts are committed.
- Generated code (`gen/` + `user/`) is committed to keep builds self-contained.
- Reports (`tools/*/ui/reports/*.json`) are generated per run and may be ignored.
