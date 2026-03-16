Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: release-pinned UI architecture inventory for convergence and platform formalization

# UI Surface Map

## Summary

- governed_surface_count: `7`
- legacy_surface_count: `73`
- fingerprint: `af5a0043c5dae97783d9b789950a0f030879617f8982562201337187945eb108`

## Governed Runtime UI Surfaces

| Path | Surface | Purpose | Platform | AppShell Commands | Shared UI Model | Truth Direct | Internal Logic |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `src/appshell/rendered_stub.py` | `rendered_adapter` | Rendered-mode adapter that exposes the shared client main-menu surface or a deterministic stub. | `cross_platform` | `no` | `yes` | `no` | `no` |
| `src/appshell/tui/tui_engine.py` | `tui_adapter` | AppShell TUI adapter over command engine, logs, and derived surfaces. | `cross_platform` | `yes` | `yes` | `no` | `no` |
| `src/client/ui/inspect_panels.py` | `derived_view_surface` | Derived inspect panels over perceived/inspection artifacts. | `cross_platform` | `no` | `no` | `no` | `no` |
| `src/client/ui/main_menu_surface.py` | `rendered_menu_surface` | Derived rendered main-menu surface for client menu flows. | `cross_platform` | `no` | `yes` | `no` | `no` |
| `src/client/ui/map_views.py` | `derived_view_surface` | Derived map view artifacts for client and TUI map surfaces. | `cross_platform` | `no` | `no` | `no` | `no` |
| `src/client/ui/viewer_shell.py` | `rendered_view_surface` | Derived rendered viewer shell over map, inspection, sky, water, and orbit artifacts. | `cross_platform` | `no` | `no` | `no` | `yes` |
| `src/ui/ui_model.py` | `shared_ui_model` | Shared menu/navigation model over AppShell command descriptors and LIB manifests. | `cross_platform` | `yes` | `yes` | `no` | `no` |

## Legacy / Deferred UI Surfaces

| Path | Status | Purpose | Platform | AppShell Commands | Truth Direct | Internal Logic |
| --- | --- | --- | --- | --- | --- | --- |
| `tools/editor_gui/CMakeLists.txt` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/editor_gui/editor_gui.c` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/gui/tools_app_win32.cpp` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `windows` | `no` | `no` | `no` |
| `tools/tool_editor/ui/doc/tool_editor_ui_doc.json` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/doc/ui_doc_template_basic.json` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/doc/ui_doc_template_basic.tlv` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.cpp` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.cpp.bak1` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.cpp.bak2` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.h` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.h.bak1` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/gen/ui_tool_editor_actions_gen.h.bak2` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/registry/ui_actions_registry.json` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/ui_actions_registry.json` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/ui_doc.tlv` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/user/ui_tool_editor_actions_user.cpp` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/user/ui_tool_editor_actions_user.cpp.bak1` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/user/ui_tool_editor_actions_user.h` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/tool_editor/ui/user/ui_tool_editor_actions_user.h.bak1` | `deferred_native_or_preview` | Editor or tooling UI scaffold kept outside the governed MVP runtime surface. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_preview_host/CMakeLists.txt` | `legacy_reference_only` | Preview host scaffolding for platform UI experiments. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_preview_host/common/ui_preview_common.cpp` | `legacy_reference_only` | Preview host scaffolding for platform UI experiments. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_preview_host/common/ui_preview_common.h` | `legacy_reference_only` | Preview host scaffolding for platform UI experiments. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_preview_host/linux/ui_preview_host_linux.cpp` | `legacy_reference_only` | Preview host scaffolding for platform UI experiments. | `linux` | `no` | `no` | `no` |
| `tools/ui_preview_host/macos/ui_preview_host_macos.cpp` | `legacy_reference_only` | Preview host scaffolding for platform UI experiments. | `macos` | `no` | `no` | `no` |
| `tools/ui_preview_host/win32/ui_preview_host_win32.cpp` | `legacy_reference_only` | Preview host scaffolding for platform UI experiments. | `windows` | `no` | `no` | `no` |
| `tools/ui_shared/include/dui/domui_event.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/include/dui/dui_api_v1.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/include/dui/dui_schema_tlv.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/include/dui/dui_win32.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `windows` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_caps.c` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_dgfx.c` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_event_queue.c` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_event_queue.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_gtk.c` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `linux` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_macos.c` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `macos` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_null.c` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_schema_parse.c` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_schema_parse.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/dui/dui_win32.c` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `windows` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_codegen/CMakeLists.txt` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_codegen/ui_codegen.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_codegen/ui_codegen.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_codegen/ui_codegen_main.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/CMakeLists.txt` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_caps.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_caps.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_diag.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_diag.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_doc.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_doc.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_fileio.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_fileio.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_json.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_json.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_legacy_import.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_legacy_import.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_props.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_props.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_string.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_string.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_tlv.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_tlv.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_types.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ir_types.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_layout.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_layout.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ops.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_ops.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_validate.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_validate.h` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/ui_shared/src/ui_ir/ui_validate_main.cpp` | `legacy_reference_only` | Legacy cross-platform UI support library and adapter scaffolding. | `cross_platform` | `no` | `no` | `no` |
| `tools/xstack/sessionx/ui_host.py` | `contradictory_legacy_host` | Legacy headless UI host outside the governed AppShell runtime surface. | `cross_platform` | `no` | `yes` | `yes` |
