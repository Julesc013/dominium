# Setup2 Error Taxonomy (SR-1)

## Domains
- `0` none
- `1` kernel
- `2` services
- `3` frontend

## Codes
- `0` OK
- `1` INVALID_ARGS
- `2` PARSE_ERROR
- `3` VALIDATION_ERROR
- `4` UNSUPPORTED_VERSION
- `5` INTEGRITY_ERROR
- `6` IO_ERROR
- `7` UNSUPPORTED_PLATFORM
- `100` INTERNAL_ERROR

## Subcodes
- `0` NONE
- `1` TLV_BAD_MAGIC
- `2` TLV_BAD_ENDIAN
- `3` TLV_BAD_HEADER_SIZE
- `4` TLV_BAD_PAYLOAD_SIZE
- `5` TLV_BAD_CRC
- `6` TLV_TRUNCATED
- `7` MISSING_FIELD
- `8` INVALID_FIELD
- `9` REQUEST_MISMATCH
- `10` SPLAT_NOT_FOUND

## Flags
- `0x0001` RETRYABLE
- `0x0002` USER_ACTIONABLE
- `0x0004` FATAL

## Exit code mapping
- `OK` -> `0`
- `error` -> `code & 0xFF` (non-zero)
