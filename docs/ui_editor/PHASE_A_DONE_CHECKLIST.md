# Phase A UI Editor — Done Checklist

## Build (pass/fail)
- `cmake -S . -B build`
- `cmake --build build --target dominium-launcher`
- `cmake --build build --target dominium-ui-editor`
- `cmake --build build --target dominium-tool-editor`

## Tests (pass/fail)
- `ctest --test-dir build -C Debug`

## Smoke (manual, pass/fail)
- Launch UI Editor; create a new UI doc; add a widget; save.
- Re-open the saved `ui_doc.tlv`; verify JSON mirror exists and matches.
- Run Validate; diagnostics appear in the log.
- Trigger codegen on save; generated files update without overwriting user edits.

## Expected artifacts
- `docs/ui_editor/fixtures/fixture_abs.tlv`
- `docs/ui_editor/fixtures/fixture_abs.json`
- `docs/ui_editor/fixtures/fixture_dock.tlv`
- `docs/ui_editor/fixtures/fixture_dock.json`
- `docs/ui_editor/fixtures/fixture_tabs_split_scroll.tlv`
- `docs/ui_editor/fixtures/fixture_tabs_split_scroll.json`
- `docs/ui_editor/fixtures/fixture_legacy_import_expected.json`
