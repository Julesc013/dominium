Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UI Editor Import/Export

## Definitions
- Canonical UI Doc: `ui_doc.tlv` plus `ui_doc.json` mirror under `tools/<tool>/ui/doc/`.
- Legacy UI: any non-canonical TLV (for example `launcher_ui_v1.tlv` or `*_ui_v*.tlv`).
- Tool UI Root: `tools/<tool>/ui/`.

## Import (Legacy -> Canonical)
- Legacy files are never modified.
- Import uses the existing legacy importer (`domui_doc_import_legacy_launcher_tlv`).
- Default destination: `tools/<tool>/ui/doc/<tool>_ui_doc.tlv` (editable in the dialog).
- Outputs are written atomically:
  - `ui_doc.tlv`
  - `ui_doc.json`
  - `import_report.json`

### Guarantees
- Deterministic ordering and stable ID remap policy.
- Unmappable or approximated legacy fields are preserved as `legacy.*` properties.

### Limitations
- Legacy importer targets the launcher UI schema format.
- Some legacy constructs are approximated (for example, stack layouts map to `ABSOLUTE`).
- Unknown legacy node kinds map to `CONTAINER` with warnings.

## Export (Canonical -> Tool-consumed)
- Export is blocked if validation reports errors.
- Default destination: `tools/<tool>/ui/ui_doc.tlv` (editable in the dialog).
- Export writes TLV + JSON mirror and runs codegen.
- If the export target is a canonical doc path and already exists, the editor warns before overwrite.
- Legacy UI files are never deleted or replaced unless explicitly selected.

## Example import report
```json
{
  "source": "source/dominium/launcher/ui_schema/launcher_ui_v1.tlv",
  "destination": "tools/launcher/ui/doc/launcher_ui_doc.tlv",
  "warnings": [
    "legacy stack layout mapped to ABSOLUTE",
    "legacy id remapped [widget 12]"
  ],
  "errors": [],
  "id_map": {
    "12": 1001
  }
}
```