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

## Semantics
- Events are emitted in deterministic order.
- Failure events include the error taxonomy fields.
- `END` always appears and mirrors the command result.
