# Setup2 Audit Model (SR-4)

Every kernel command emits `setup_audit.tlv` even on failure.

## Event IDs (ordered)
- `1` BEGIN
- `2` PARSE_MANIFEST_OK
- `3` PARSE_MANIFEST_FAIL
- `4` PARSE_REQUEST_OK
- `5` PARSE_REQUEST_FAIL
- `6` SPLAT_SELECT_OK
- `7` SPLAT_SELECT_FAIL
- `8` PLAN_RESOLVE_OK
- `9` PLAN_RESOLVE_FAIL
- `10` PLAN_BUILD_OK
- `11` PLAN_BUILD_FAIL
- `12` WRITE_STATE_OK
- `13` WRITE_STATE_FAIL
- `14` END
- `15` APPLY_BEGIN
- `16` STAGE_OK
- `17` STAGE_FAIL
- `18` VERIFY_OK
- `19` VERIFY_FAIL
- `20` COMMIT_OK
- `21` COMMIT_FAIL
- `22` REGISTER_OK
- `23` REGISTER_FAIL
- `24` WRITE_AUDIT_OK
- `25` WRITE_AUDIT_FAIL
- `26` ROLLBACK_BEGIN
- `27` ROLLBACK_STEP_OK
- `28` ROLLBACK_STEP_FAIL
- `29` ROLLBACK_END
- `30` RESUME_BEGIN
- `31` RESUME_END
- `32` IMPORT_BEGIN
- `33` IMPORT_PARSE_OK
- `34` IMPORT_PARSE_FAIL
- `35` IMPORT_WRITE_STATE_OK
- `36` IMPORT_WRITE_STATE_FAIL
- `37` IMPORT_END
- `38` SPLAT_DEPRECATED

## Semantics
- Events are emitted in deterministic order.
- Failure events include the error taxonomy fields.
- `END` always appears and mirrors the command result.
- `SPLAT_DEPRECATED` is emitted when a deprecated SPLAT is selected.
