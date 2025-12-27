# Dominium Setup CLI JSON Schemas (v1)

This document locks the **v1 JSON contract** for `dominium-setup`.

Constraints:

- Stable key ordering (as written below).
- No floats (all numbers are integers).
- Paths are normalized to `/` separators.
- In deterministic mode (`--deterministic 1`, default), timestamps are `0` and array ordering is canonical.
- All JSON is UTF-8.

## Common envelope (all JSON-capable commands)

All JSON-capable commands output **one JSON object** to `stdout`.

Exception (current behavior):

- `dry-run`, `install`, `uninstall`, `platform-register`, and `platform-unregister`
  emit a minimal JSON object without the standard envelope.

Key ordering is fixed:

1. `schema_version` (number)
2. `command` (string)
3. `status` (string)
4. `status_code` (number)
5. `details` (object)

```json
{
  "schema_version": 1,
  "command": "apply",
  "status": "ok",
  "status_code": 0,
  "details": {}
}
```

### `schema_version`

- `1` for CLI v1.

### `status_code` and `status`

`status_code` is the process exit code and is stable:

- `0` → `status="ok"`
- `1` → `status="error"`
- `2` → `status="verification_failed"`
- `3` → `status="invalid_input"`
- `4` → `status="unsupported"`
- `5` → `status="partial_success"`

### `details.core_status` / `details.core_status_name`

Most commands include core status for diagnostics:

- `core_status`: numeric `dsu_status_t`
- `core_status_name`: stable string name (e.g. `"success"`, `"invalid_args"`, `"parse_error"`, `"integrity_error"`)

## Field conventions

### Hex digests (`*_digest64`, `journal_id`, …)

64-bit digests are emitted as a fixed-width lowercase hex string:

- `"0x" + 16 hex digits` (e.g. `"0x0000000000000000"`)

Invocation digest fields:

- `invocation_digest64` is computed from the canonical invocation payload
  (see `docs/setup/INVOCATION_PAYLOAD.md`).

### Paths

JSON paths are emitted as strings with `/` separators (even on Windows).

## Command schemas

### `version`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `name`
4. `version`

### `manifest validate`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `in_file`
4. `content_digest32`
5. `content_digest64`
6. `error`

### `manifest dump`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `in_file`
4. `out_file`
5. `content_digest32`
6. `content_digest64`
7. `wrote_file`
8. `error`
9. `manifest` (optional; present when `out_file==""`)

`details.manifest` is the canonical JSON manifest object (see `docs/setup/MANIFEST_SCHEMA.md`).

### `resolve`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `operation`
4. `scope`
5. `platform`
6. `invocation_digest64`
7. `allow_prerelease`
8. `product_id`
9. `product_version`
10. `install_root`
11. `manifest_digest64`
12. `resolved_digest64`
13. `components` (array)
14. `log` (array)

`details.components[]` key order:

1. `component_id`
2. `version`
3. `source`
4. `action`

`details.log[]` key order:

1. `event`
2. `a`
3. `b`

### `plan`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `deterministic`
4. `operation`
5. `scope`
6. `platform`
7. `invocation_digest64`
8. `manifest_digest64`
9. `resolved_digest64`
10. `plan_file`
11. `plan_id_hash32`
12. `plan_id_hash64`
13. `component_count`
14. `step_count`
15. `error`

### `apply`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `deterministic`
4. `dry_run`
5. `log_file`
6. (on success) `plan_file`, `plan_digest64`, `invocation_digest64`, `journal_id`, `install_root`, `txn_root`, `journal_file`, `journal_entry_count`, `commit_progress`, `staged_file_count`, `verified_ok`, `verified_missing`, `verified_mismatch`, `error`
7. (on failure) `error`

### `export-invocation`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `manifest_file`
4. `invocation_file`
5. `invocation_digest64`
6. `operation`
7. `scope`
8. `platform`
9. `error`

### `apply-invocation`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `deterministic`
4. `dry_run`
5. `invocation_file`
6. `invocation_digest64`
7. `plan_file`
8. `plan_digest64`
9. `journal_id`
10. `install_root`
11. `txn_root`
12. `journal_file`
13. `journal_entry_count`
14. `commit_progress`
15. `staged_file_count`
16. `verified_ok`
17. `verified_missing`
18. `verified_mismatch`
19. `error`

### `dry-run` (minimal object)

Key order (success):

1. `command`
2. `status`
3. `deterministic`
4. `plan_file`
5. `log_file`
6. `plan_id_hash32`
7. `plan_id_hash64`
8. `step_count`

On failure, the object contains: `command`, `status`, `error`, `exit_code`.

### `install` (minimal object)

Key order:

1. `command`
2. `status`
3. `error`
4. `exit_code`
5. `deterministic`
6. `dry_run`
7. `log_file`
8. (on success) `plan_file`, `plan_id_hash64`, `journal_id`, `install_root`, `txn_root`, `journal_file`, `journal_entry_count`, `commit_progress`, `staged_file_count`, `verified_ok`, `verified_missing`, `verified_mismatch`

### `uninstall` (minimal object)

Key order:

1. `command`
2. `status`
3. `error`
4. `exit_code`
5. `deterministic`
6. `dry_run`
7. `log_file`
8. (on success) `state_file`, `journal_id`, `install_root`, `txn_root`, `journal_file`, `journal_entry_count`, `commit_progress`

### `verify`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `state_file`
4. `format`
5. `checked`
6. `ok`
7. `missing`
8. `modified`
9. `extra`
10. `errors`
11. `report` (object or `null`)
12. `error`

Exit code is `2` when any of `missing/modified/extra/errors` is non-zero.

### `list-installed` (alias: `list`)

Schema is identical for both commands; the envelope `command` value is `list-installed` or `list` based on invocation.

`details` key order:

1. `core_status`
2. `core_status_name`
3. `state_file`
4. `format`
5. `report` (object or `null`)
6. `error`

### `report`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `state_file`
4. `out_dir`
5. `format`
6. `verify_checked`
7. `verify_ok`
8. `verify_missing`
9. `verify_modified`
10. `verify_extra`
11. `verify_errors`
12. `reports` (array)
13. `error`

`details.reports[]` key order:

1. `name`
2. `file`

### `uninstall-preview`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `state_file`
4. `format`
5. `components` (array of strings; the requested subset, possibly empty)
6. `report` (object or `null`)
7. `error`

### `rollback`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `deterministic`
4. `dry_run`
5. `journal_file`
6. (on success) `journal_id`, `plan_digest64`, `install_root`, `txn_root`, `journal_entry_count`, `commit_progress_before`, `error`
7. (on failure) `error`

### `export-log`

`details` key order:

1. `core_status`
2. `core_status_name`
3. `log_file`
4. `out_file`
5. `format`
6. `event_count`
7. `error`

The exported JSON log file schema is documented in `docs/setup/AUDIT_LOG_FORMAT.md`.

### `platform-register`

Minimal JSON object key order:

1. `command`
2. `state_file`
3. `status`
4. `error` (present only on failure)

### `platform-unregister`

Minimal JSON object key order:

1. `command`
2. `state_file`
3. `status`
4. `error` (present only on failure)

## See also

- `docs/setup/CLI_REFERENCE.md`
- `docs/setup/AUDIT_LOG_FORMAT.md`
