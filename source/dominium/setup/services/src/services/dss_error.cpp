#include "dss/dss_error.h"

extern "C" {

dss_error_t dss_error_make(dss_u16 domain,
                           dss_u16 code,
                           dss_u16 subcode,
                           dss_u16 flags) {
    dss_error_t err;
    err.domain = domain;
    err.code = code;
    err.subcode = subcode;
    err.flags = flags;
    return err;
}

int dss_error_is_ok(dss_error_t err) {
    return err.code == DSS_CODE_OK;
}

const char *dss_error_to_string_stable(dss_error_t err) {
    switch (err.code) {
    case DSS_CODE_OK:
        return "ok";
    case DSS_CODE_INVALID_ARGS:
        return "invalid_args";
    case DSS_CODE_IO:
        return "io_error";
    case DSS_CODE_PERMS:
        return "perms_error";
    case DSS_CODE_PROC:
        return "proc_error";
    case DSS_CODE_ARCHIVE:
        return "archive_error";
    case DSS_CODE_HASH:
        return "hash_error";
    case DSS_CODE_PLATFORM:
        return "platform_error";
    case DSS_CODE_NOT_SUPPORTED:
        return "not_supported";
    case DSS_CODE_SANDBOX_VIOLATION:
        return "sandbox_violation";
    case DSS_CODE_NOT_FOUND:
        return "not_found";
    case DSS_CODE_INTERNAL:
    default:
        return "internal_error";
    }
}

static dsk_u16 dss_map_code_to_dsk(dss_u16 code) {
    switch (code) {
    case DSS_CODE_OK:
        return DSK_CODE_OK;
    case DSS_CODE_INVALID_ARGS:
        return DSK_CODE_INVALID_ARGS;
    case DSS_CODE_IO:
    case DSS_CODE_NOT_FOUND:
    case DSS_CODE_SANDBOX_VIOLATION:
        return DSK_CODE_IO_ERROR;
    case DSS_CODE_PLATFORM:
        return DSK_CODE_UNSUPPORTED_PLATFORM;
    case DSS_CODE_ARCHIVE:
    case DSS_CODE_HASH:
    case DSS_CODE_PROC:
    case DSS_CODE_PERMS:
    case DSS_CODE_NOT_SUPPORTED:
    case DSS_CODE_INTERNAL:
    default:
        return DSK_CODE_INTERNAL_ERROR;
    }
}

dsk_error_t dss_to_dsk_error(dss_error_t err) {
    if (dss_error_is_ok(err)) {
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    return dsk_error_make(DSK_DOMAIN_SERVICES,
                          dss_map_code_to_dsk(err.code),
                          err.subcode,
                          err.flags);
}

} /* extern "C" */
