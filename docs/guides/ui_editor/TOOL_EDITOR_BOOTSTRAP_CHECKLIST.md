Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Tool Editor Bootstrap — Done Checklist

## Build (pass/fail)
- `cmake -S . -B build`
- `cmake --build build --target dominium-tool-editor`

## Tests (pass/fail)
- `ctest --test-dir build -C Debug`

## Smoke (manual, pass/fail)
- Launch Tool Editor; confirm it loads `tool_editor_ui_doc.tlv`.
- Open an existing `ui_doc.tlv`, edit a widget property, save.
- Verify JSON mirror updated alongside TLV.
- Create a new doc from `ui_doc_template_basic.tlv`, save, reopen.

## Expected artifacts
- `tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv`
- `tools/tool_editor/ui/doc/tool_editor_ui_doc.json`
- `tools/tool_editor/ui/doc/ui_doc_template_basic.tlv`