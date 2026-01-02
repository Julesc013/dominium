#ifndef DSS_ERROR_H
#define DSS_ERROR_H

#include "dss_types.h"
#include "dsk/dsk_error.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dss_error_t {
    dss_u16 domain;
    dss_u16 code;
    dss_u16 subcode;
    dss_u16 flags;
} dss_error_t;

typedef dss_error_t dss_status_t;

#define DSS_DOMAIN_SERVICES DSK_DOMAIN_SERVICES

/* Codes */
#define DSS_CODE_OK 0u
#define DSS_CODE_INVALID_ARGS 1u
#define DSS_CODE_IO 2u
#define DSS_CODE_PERMS 3u
#define DSS_CODE_PROC 4u
#define DSS_CODE_ARCHIVE 5u
#define DSS_CODE_HASH 6u
#define DSS_CODE_PLATFORM 7u
#define DSS_CODE_NOT_SUPPORTED 8u
#define DSS_CODE_SANDBOX_VIOLATION 9u
#define DSS_CODE_NOT_FOUND 10u
#define DSS_CODE_INTERNAL 100u

/* Subcodes */
#define DSS_SUBCODE_NONE 0u
#define DSS_SUBCODE_PATH_TRAVERSAL 1u
#define DSS_SUBCODE_OUTSIDE_SANDBOX 2u

/* Flags (shared with kernel taxonomy). */
#define DSS_ERROR_FLAG_RETRYABLE DSK_ERROR_FLAG_RETRYABLE
#define DSS_ERROR_FLAG_USER_ACTIONABLE DSK_ERROR_FLAG_USER_ACTIONABLE
#define DSS_ERROR_FLAG_FATAL DSK_ERROR_FLAG_FATAL

DSS_API dss_error_t dss_error_make(dss_u16 domain,
                                   dss_u16 code,
                                   dss_u16 subcode,
                                   dss_u16 flags);

DSS_API int dss_error_is_ok(dss_error_t err);
DSS_API const char *dss_error_to_string_stable(dss_error_t err);
DSS_API dsk_error_t dss_to_dsk_error(dss_error_t err);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSS_ERROR_H */
