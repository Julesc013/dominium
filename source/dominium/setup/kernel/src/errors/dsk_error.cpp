#include "dsk/dsk_error.h"

static u32 dsk_msg_id_from_code(dsk_u16 code) {
    switch (code) {
    case DSK_CODE_INVALID_ARGS: return (u32)ERRMSG_COMMON_INVALID_ARGS;
    case DSK_CODE_PARSE_ERROR: return (u32)ERRMSG_TLV_PARSE_FAILED;
    case DSK_CODE_VALIDATION_ERROR: return (u32)ERRMSG_TLV_MISSING_FIELD;
    case DSK_CODE_UNSUPPORTED_VERSION: return (u32)ERRMSG_TLV_SCHEMA_VERSION;
    case DSK_CODE_INTEGRITY_ERROR: return (u32)ERRMSG_TLV_INTEGRITY;
    case DSK_CODE_IO_ERROR: return (u32)ERRMSG_FS_WRITE_FAILED;
    case DSK_CODE_UNSUPPORTED_PLATFORM: return (u32)ERRMSG_SETUP_UNSUPPORTED_PLATFORM;
    case DSK_CODE_INTERNAL_ERROR: return (u32)ERRMSG_COMMON_INTERNAL;
    case DSK_CODE_OK: default: return (u32)ERRMSG_NONE;
    }
}

dsk_error_t dsk_error_make(dsk_u16 domain,
                           dsk_u16 code,
                           dsk_u16 subcode,
                           dsk_u16 flags) {
    u16 err_domain = (domain == (dsk_u16)DSK_DOMAIN_NONE) ? (u16)ERRD_NONE : (u16)ERRD_SETUP;
    err_t err = err_make(err_domain, code, (u32)flags, dsk_msg_id_from_code(code));
    if (subcode != 0u) {
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SUBCODE, (u32)subcode);
    }
    return err;
}

int dsk_error_is_ok(dsk_error_t err) {
    return err_is_ok(&err);
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
