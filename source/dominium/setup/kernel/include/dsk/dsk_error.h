#ifndef DSK_ERROR_H
#define DSK_ERROR_H

#include "dsk_types.h"
#include "dominium/core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef err_t dsk_error_t;
typedef err_t dsk_status_t;

/* Domains */
#define DSK_DOMAIN_NONE ERRD_NONE
#define DSK_DOMAIN_KERNEL ERRD_SETUP
#define DSK_DOMAIN_SERVICES ERRD_SETUP
#define DSK_DOMAIN_FRONTEND ERRD_SETUP

/* Codes */
#define DSK_CODE_OK 0u
#define DSK_CODE_INVALID_ARGS 1u
#define DSK_CODE_PARSE_ERROR 2u
#define DSK_CODE_VALIDATION_ERROR 3u
#define DSK_CODE_UNSUPPORTED_VERSION 4u
#define DSK_CODE_INTEGRITY_ERROR 5u
#define DSK_CODE_IO_ERROR 6u
#define DSK_CODE_UNSUPPORTED_PLATFORM 7u
#define DSK_CODE_INTERNAL_ERROR 100u

/* Subcodes */
#define DSK_SUBCODE_NONE 0u
#define DSK_SUBCODE_TLV_BAD_MAGIC 1u
#define DSK_SUBCODE_TLV_BAD_ENDIAN 2u
#define DSK_SUBCODE_TLV_BAD_HEADER_SIZE 3u
#define DSK_SUBCODE_TLV_BAD_PAYLOAD_SIZE 4u
#define DSK_SUBCODE_TLV_BAD_CRC 5u
#define DSK_SUBCODE_TLV_TRUNCATED 6u
#define DSK_SUBCODE_MISSING_FIELD 7u
#define DSK_SUBCODE_INVALID_FIELD 8u
#define DSK_SUBCODE_REQUEST_MISMATCH 9u
#define DSK_SUBCODE_SPLAT_NOT_FOUND 10u
#define DSK_SUBCODE_NO_COMPATIBLE_SPLAT 11u
#define DSK_SUBCODE_COMPONENT_NOT_FOUND 12u
#define DSK_SUBCODE_UNSATISFIED_DEPENDENCY 13u
#define DSK_SUBCODE_EXPLICIT_CONFLICT 14u
#define DSK_SUBCODE_PLATFORM_INCOMPATIBLE 15u
#define DSK_SUBCODE_PLAN_DIGEST_MISMATCH 16u
#define DSK_SUBCODE_PLAN_RESOLVED_DIGEST_MISMATCH 17u

/* Flags */
#define DSK_ERROR_FLAG_RETRYABLE ERRF_RETRYABLE
#define DSK_ERROR_FLAG_USER_ACTIONABLE ERRF_USER_ACTIONABLE
#define DSK_ERROR_FLAG_FATAL ERRF_FATAL

DSK_API dsk_error_t dsk_error_make(dsk_u16 domain,
                                   dsk_u16 code,
                                   dsk_u16 subcode,
                                   dsk_u16 flags);

DSK_API int dsk_error_is_ok(dsk_error_t err);
DSK_API const char *dsk_error_to_string_stable(dsk_error_t err);
DSK_API int dsk_error_to_exit_code(dsk_error_t err);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSK_ERROR_H */
