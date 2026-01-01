# Legacy State Import

Setup2 can import legacy DSU installed state into `installed_state.tlv`.

## Kernel API
- `dsk_import_legacy_state` consumes legacy bytes and emits Setup2 state + audit.
- Deterministic mode sets `run_id=0`.

## CLI
```
dominium-setup2 import-legacy-state --in <legacy_state> --out <installed_state> --out-audit <setup_audit.tlv> --deterministic 1
```

## Mapping rules
- Preserve component list (normalized to lowercase).
- Map ownership conservatively to `portable` when unknown.
- Set `import_source` to `legacy_dsu_state_v1` or `legacy_dsu_state_v2`.
- Populate `import_details` with mapping decisions and legacy metadata.

## Audit behavior
- Audit events: IMPORT_BEGIN, IMPORT_PARSE_OK/FAIL, IMPORT_WRITE_STATE_OK/FAIL, IMPORT_END.
- Refusal codes are stable; parsing failures return `PARSE_ERROR` subcodes.

## Constraints
- Import is read-only on legacy state.
- Unknown legacy fields are ignored deterministically.
