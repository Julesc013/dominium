# Tool Editor (Bootstrap)

Windows-only host that loads and edits `ui_doc.tlv` files using the DUI Win32 backend.

Build

- Configure: `cmake -S . -B build`
- Build: `cmake --build build --target dominium-tool-editor`

Run

- `build\\tools\\tool_editor\\Debug\\dominium-tool-editor.exe`

UI docs and codegen outputs

- UI doc: `tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv` (+ JSON mirror)
- Template doc: `tools/tool_editor/ui/doc/ui_doc_template_basic.tlv`
- Action registry: `tools/tool_editor/ui/registry/ui_actions_registry.json`
- Generated code: `tools/tool_editor/ui/gen/` and `tools/tool_editor/ui/user/`

Editing the Tool Editor UI

- Use the UI Editor (`dominium-ui-editor`) to open `tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv`.
- Save the doc, then rebuild `dominium-tool-editor` to regenerate action bindings.
