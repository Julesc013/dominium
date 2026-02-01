Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# SERVICES_ERRORS

Service errors use `dss_error_t` with domain `DSS_DOMAIN_SERVICES`.

Codes:
- DSS_CODE_OK: success
- DSS_CODE_INVALID_ARGS: invalid input or null pointer
- DSS_CODE_IO: filesystem or IO failure
- DSS_CODE_PERMS: permission/elevation failure
- DSS_CODE_PROC: process spawn failure
- DSS_CODE_ARCHIVE: archive parse/format/integrity failure
- DSS_CODE_HASH: hash computation failure
- DSS_CODE_PLATFORM: unsupported/unknown platform
- DSS_CODE_NOT_SUPPORTED: stubbed or unavailable capability
- DSS_CODE_SANDBOX_VIOLATION: fake FS escape or traversal
- DSS_CODE_NOT_FOUND: missing file/resource
- DSS_CODE_INTERNAL: internal error

Kernel mapping (`dss_to_dsk_error`):
- INVALID_ARGS -> DSK_CODE_INVALID_ARGS
- IO / NOT_FOUND / SANDBOX_VIOLATION -> DSK_CODE_IO_ERROR
- PLATFORM -> DSK_CODE_UNSUPPORTED_PLATFORM
- ARCHIVE / HASH / PROC / PERMS / NOT_SUPPORTED / INTERNAL -> DSK_CODE_INTERNAL_ERROR