Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Dominium UI Editor CLI

This document covers headless CLI usage for `dominium-ui-editor`. Any
`--headless-*` or `--scan-ui` flag runs in CLI mode without creating windows.

## Commands

- `--help`
  - Print CLI help and exit 0.
- `--scan-ui [--out <path>]`
  - Scan the repo for UI docs and write `ui_index.json`.
- `--headless-validate <ui_doc.tlv> [--targets <list>] [--report <path.json>]`
  - Validate a UI doc in memory without modifying files.
  - `--targets` is a comma-separated list of backend or tier IDs (no spaces unless quoted).
- `--headless-format <ui_doc.tlv> [--out <ui_doc_out.tlv>] [--report <path.json>]`
  - Validate then write canonical TLV and JSON mirror (atomic + backup rotation).
- `--headless-codegen --in <ui_doc.tlv> --out <gen_dir> --registry <registry.json> --docname <name> [--report <path.json>]`
  - Validate then run action codegen and update the registry.
- `--headless-build-ui --in <ui_doc.tlv> --docname <name> --out-root <tool/ui/> [--report <path.json>]`
  - Validate, format, and codegen into a tool UI root.
- `--headless-apply <ui_doc.tlv> --script <ops.json> [--out <ui_doc_out.tlv>] [--report <path.json>] [--in-new]`
  - Apply a deterministic ops.json script to a UI doc.
  - If `--in-new` is set, start from an empty doc instead of loading the input.

## Exit Codes

- `--help`
  - `0` always
- `--scan-ui`
  - `0` success
  - `1` failure
- `--headless-validate`
  - `0` valid
  - `2` validation errors
  - `1` IO or fatal error
- `--headless-format`
  - `0` success
  - `2` validation errors
  - `1` IO failure
- `--headless-codegen`
  - `0` success
  - `2` validation errors
  - `1` other failure
- `--headless-build-ui`
  - `0` success
  - `2` validation errors
  - `1` other failure
- `--headless-apply`
  - `0` success
  - `2` validation errors
  - `3` script parse/apply errors
  - `1` IO or fatal error

## Reports (--report)

All headless commands accept `--report <path.json>`. Reports are deterministic:

- Arrays are sorted.
- No timestamps.
- Paths are repo-relative when possible (or CWD-relative, else basename).

Base schema:

```json
{
  "command": "headless-validate",
  "input": "tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv",
  "output_files": [],
  "errors": [],
  "warnings": [],
  "created_ids": {},
  "exit_code": 0
}
```

Reports include `status` for all commands; validation reports also include `targets`.

### Sample validation report

```json
{
  "command": "headless-validate",
  "input": "tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv",
  "output_files": [],
  "errors": [],
  "warnings": [],
  "created_ids": {},
  "exit_code": 0,
  "status": "ok",
  "targets": [
    "win32"
  ]
}
```

### Sample format report

```json
{
  "command": "headless-format",
  "input": "tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv",
  "output_files": [
    "tools/tool_editor/ui/doc/tool_editor_ui_doc.json",
    "tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv"
  ],
  "errors": [],
  "warnings": [],
  "created_ids": {},
  "exit_code": 0,
  "status": "ok"
}
```

### Sample apply report

```json
{
  "command": "headless-apply",
  "input": "tools/launcher/ui/doc/launcher_ui_doc.tlv",
  "output_files": [
    "tools/launcher/ui/doc/launcher_ui_doc.json",
    "tools/launcher/ui/doc/launcher_ui_doc.tlv"
  ],
  "errors": [],
  "warnings": [],
  "created_ids": {
    "root": 1,
    "play_button": 7
  },
  "exit_code": 0,
  "status": "ok"
}
```

## Examples

```
dominium-ui-editor --help
dominium-ui-editor --scan-ui --out tools/ui_index/ui_index.json
dominium-ui-editor --headless-validate tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv --report out/validate.json
dominium-ui-editor --headless-format tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv --report out/format.json
dominium-ui-editor --headless-codegen --in tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv --out tools/tool_editor/ui/gen --registry tools/tool_editor/ui/registry/ui_actions_registry.json --docname tool_editor_ui_doc
dominium-ui-editor --headless-build-ui --in tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv --docname tool_editor_ui_doc --out-root tools/tool_editor/ui
dominium-ui-editor --headless-apply tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv --script ops.json --report out/apply.json
```