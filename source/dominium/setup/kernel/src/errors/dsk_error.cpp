#include "dsk/dsk_error.h"

dsk_error_t dsk_error_make(dsk_u16 domain,
                           dsk_u16 code,
                           dsk_u16 subcode,
                           dsk_u16 flags) {
    dsk_error_t err;
    err.domain = domain;
    err.code = code;
    err.subcode = subcode;
    err.flags = flags;
    return err;
}

int dsk_error_is_ok(dsk_error_t err) {
    return err.domain == DSK_DOMAIN_NONE && err.code == DSK_CODE_OK;
}

const char *dsk_error_to_string_stable(dsk_error_t err) {
    switch (err.code) {
    case DSK_CODE_OK: return "ok";
    case DSK_CODE_INVALID_ARGS: return "invalid_args";
    case DSK_CODE_PARSE_ERROR: return "parse_error";
    case DSK_CODE_VALIDATION_ERROR: return "validation_error";
    case DSK_CODE_UNSUPPORTED_VERSION: return "unsupported_version";
    case DSK_CODE_INTEGRITY_ERROR: return "integrity_error";
    case DSK_CODE_IO_ERROR: return "io_error";
    case DSK_CODE_UNSUPPORTED_PLATFORM: return "unsupported_platform";
    case DSK_CODE_INTERNAL_ERROR: return "internal_error";
    default: return "unknown_error";
    }
}

int dsk_error_to_exit_code(dsk_error_t err) {
    if (dsk_error_is_ok(err)) {
        return 0;
    }
    if (err.code == 0u) {
        return 1;
    }
    return (int)(err.code & 0xFFu);
}
