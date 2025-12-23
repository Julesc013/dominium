# UI Editor (Phase A)

Phase A delivers a Windows-only Win32 UI Editor for authoring `ui_doc.tlv`.
It supports live preview via the DUI Win32 backend, validation, and action codegen.

What it is:
- New/Open/Save/Save As with atomic saves and JSON mirror output.
- Hierarchy tree with search, canvas preview, property inspector, and diagnostics log.
- Codegen on save: `doc/` for TLV+JSON, plus `gen/`, `user/`, and `registry/` at the doc root.
- Canvas selection overlay with drag and keyboard nudges (Shift = 10px).

What it is not:
- No cross-platform editor.
- No DPI scaling, advanced docking, or performance tuning beyond correctness.
- No Tool Editor UI (Phase B still a stub).
- Docked widgets are edited via properties (dragging is disabled).

Smoke checklist:
1) New doc → add widgets → set dock/anchors → Save → reload.
2) Preview resizes; selection/move/resize and Shift-nudge update layout deterministically; search selects widgets.
3) Validate shows warnings/errors in the log and selects widgets.
4) Save triggers codegen and generated sources compile.

Manual verification

- See `docs/ui_editor/FLICKER_NOTES.md` for Win32 batching/resizing checks.
- If built with the MSYS2 presets, ensure `C:\msys64\ucrt64\bin` is on PATH when running `domui_validate.exe` or `domui_codegen.exe`.
- Smoke run: not executed in this environment (GUI run required).
- Build note: `dominium-ui-editor` link failed here because the EXE was running (LNK1168). Close it and rebuild.

Checklists

- `docs/ui_editor/PHASE_A_DONE_CHECKLIST.md`
- `docs/ui_editor/TOOL_EDITOR_BOOTSTRAP_CHECKLIST.md`
