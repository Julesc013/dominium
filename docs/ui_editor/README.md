# UI Editor (Phase A)

Phase A delivers a Windows-only Win32 UI Editor for authoring `ui_doc.tlv`.
It supports live preview via the DUI Win32 backend, validation, and action codegen.

What it is:
- New/Open/Save/Save As with atomic saves and JSON mirror output.
- Hierarchy tree, canvas preview, property inspector, and diagnostics log.
- Codegen on save: `ui_actions_registry.json`, `gen/`, and `user/` next to the TLV.

What it is not:
- No cross-platform editor.
- No DPI scaling, advanced docking, or performance tuning beyond correctness.
- No Tool Editor UI (Phase B still a stub).

Smoke checklist:
1) New doc → add widgets → set dock/anchors → Save → reload.
2) Preview resizes; selection/move/resize updates layout deterministically.
3) Validate shows warnings/errors in the log and selects widgets.
4) Save triggers codegen and generated sources compile.

Manual verification

- See `docs/ui_editor/FLICKER_NOTES.md` for Win32 batching/resizing checks.
