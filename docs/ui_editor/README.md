# UI Editor Scaffolding

Phase A: UI Editor (Windows-only, Win32 stub) with minimal window and build wiring.
Phase A goal: establish targets and shared libraries without changing runtime UI behavior.
Phase A scope: scaffolding only, no schema changes or generator changes.

Phase B: Tool Editor placeholder executable with minimal stub entrypoint.
Phase B goal: reserve a target and future integration points.

Shared libraries: domino_ui_ir and domino_ui_codegen are stubs for UI IR and codegen.
No external UI frameworks; Win32 only for now.
C89/C++98 compatibility remains required.

See REPO_MAP_UI_SYSTEM.md for the current UI system map.
See SPEC_UI_DOC_TLV.md for the future TLV document spec outline.
