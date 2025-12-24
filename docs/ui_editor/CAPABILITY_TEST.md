# UI Capability Test (Minecraft-Structure)

This is the pass/fail gate for the UI Editor toolchain and the Minecraft-structure
launcher/setup UIs. All steps are headless and deterministic.

## Commands

```
cmake --build build\msvc-debug --config Debug --target ui_capability_test
cmake --build build\msvc-debug --config Debug --target dominium-launcher
cmake --build build\msvc-debug --config Debug --target dominium-setup
ctest --test-dir build\msvc-debug -C Debug -R test_ui_ --output-on-failure
```

## Pass/Fail Checklist

- `ui_scan_all` generates `tools/ui_index/ui_index.json`.
- `ui_regen_launcher` regenerates launcher doc, JSON mirror, codegen outputs, and reports.
- `ui_regen_setup` regenerates setup doc, JSON mirror, codegen outputs, and reports.
- `ui_validate_all` validates launcher and setup docs with `win32_t1` targets (exit 0).
- `dominium-launcher` and `dominium-setup` compile with generated stubs.
- Determinism tests pass (apply, codegen, registry stability, ui_index).

## Outputs (Expected)

- `tools/launcher/ui/doc/launcher_ui_doc.tlv`
- `tools/launcher/ui/doc/launcher_ui_doc.json`
- `tools/launcher/ui/gen/ui_launcher_ui_actions_gen.*`
- `tools/launcher/ui/user/ui_launcher_ui_actions_user.*`
- `tools/launcher/ui/registry/launcher_actions_registry.json`
- `tools/launcher/ui/reports/*.json`
- `tools/setup/ui/doc/setup_ui_doc.tlv`
- `tools/setup/ui/doc/setup_ui_doc.json`
- `tools/setup/ui/gen/ui_setup_ui_actions_gen.*`
- `tools/setup/ui/user/ui_setup_ui_actions_user.*`
- `tools/setup/ui/registry/setup_actions_registry.json`
- `tools/setup/ui/reports/*.json`
