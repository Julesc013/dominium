Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: release-pinned UI architecture inventory for platform formalization

# UI Reconcile Final

## Current UI Surfaces

- governed_runtime_surfaces: `7`
- legacy_or_preview_surfaces: `73`
- violations: `0`
- fingerprint: `af5a0043c5dae97783d9b789950a0f030879617f8982562201337187945eb108`

## Enabled By Platform

| Platform | Client Rendered | Launcher Native | Setup Native | TUI | CLI | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `windows` | `yes` | `no` | `no` | `yes` | `yes` | native disabled -> rendered/TUI/CLI fallback |
| `macos` | `yes` | `no` | `no` | `yes` | `yes` | native disabled -> rendered/TUI/CLI fallback |
| `linux` | `yes` | `no` | `no` | `yes` | `yes` | native disabled -> rendered/TUI/CLI fallback |

## Deferred

- `tools/editor_gui/CMakeLists.txt` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/editor_gui/editor_gui.c` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/gui/tools_app_win32.cpp` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/doc/tool_editor_ui_doc.json` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/doc/ui_doc_template_basic.json` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/doc/ui_doc_template_basic.tlv` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.cpp` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.cpp.bak1` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.cpp.bak2` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.h` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.
- `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.h.bak1` `deferred_native_or_preview`: Editor or tooling UI scaffold kept outside the governed MVP runtime surface.

## Enforcement

- No governed UI adapter violations were detected.

## Readiness

- Shared menu/navigation state is centralized in `src/ui/ui_model.py`.
- Rendered and TUI adapters now bind through the shared model without changing the locked viewer-shell truth/view contract.
- Governed native adapters remain capability-disabled until PLATFORM-FORMALIZE-0 provides concrete platform bindings.
