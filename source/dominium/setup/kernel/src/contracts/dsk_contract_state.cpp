/*
FILE: source/dominium/setup/kernel/src/contracts/dsk_contract_state.cpp
MODULE: Dominium
PURPOSE: Setup installed_state wrappers (delegates to core_installed_state).
*/

#include "dsk/dsk_contracts.h"

#include "dominium/core_installed_state.h"

static dsk_u16 dsk_subcode_from_err(const err_t* err) {
    u32 i;
    if (!err) {
        return 0u;
    }
    for (i = 0u; i < err->detail_count; ++i) {
        const err_detail* d = &err->details[i];
        if (d->key_id == (u32)ERR_DETAIL_KEY_SUBCODE &&
            d->type == (u32)ERR_DETAIL_TYPE_U32) {
            return (dsk_u16)d->v.u32_value;
        }
    }
    return 0u;
}

static dsk_status_t dsk_state_map_err(const err_t* err) {
    dsk_u16 subcode = dsk_subcode_from_err(err);
    if (!err || err_is_ok(err)) {
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    if (err->domain == (u16)ERRD_COMMON && err->code == (u16)ERRC_COMMON_INVALID_ARGS) {
        return dsk_error_make(DSK_DOMAIN_KERNEL,
                              DSK_CODE_INVALID_ARGS,
                              subcode,
                              DSK_ERROR_FLAG_USER_ACTIONABLE);
    }
    if (err->domain == (u16)ERRD_TLV) {
        if (err->code == (u16)ERRC_TLV_SCHEMA_VERSION) {
            return dsk_error_make(DSK_DOMAIN_KERNEL,
                                  DSK_CODE_UNSUPPORTED_VERSION,
                                  subcode,
                                  DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        if (err->code == (u16)ERRC_TLV_MISSING_FIELD) {
            if (subcode == 0u) {
                subcode = DSK_SUBCODE_MISSING_FIELD;
            }
            return dsk_error_make(DSK_DOMAIN_KERNEL,
                                  DSK_CODE_VALIDATION_ERROR,
                                  subcode,
                                  DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        if (err->code == (u16)ERRC_TLV_INTEGRITY) {
            return dsk_error_make(DSK_DOMAIN_KERNEL,
                                  DSK_CODE_INTEGRITY_ERROR,
                                  subcode,
                                  DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        return dsk_error_make(DSK_DOMAIN_KERNEL,
                              DSK_CODE_PARSE_ERROR,
                              subcode,
                              DSK_ERROR_FLAG_USER_ACTIONABLE);
    }
    return dsk_error_make(DSK_DOMAIN_KERNEL,
                          DSK_CODE_INTERNAL_ERROR,
                          subcode,
                          DSK_ERROR_FLAG_USER_ACTIONABLE);
}

void dsk_installed_state_clear(dsk_installed_state_t* state) {
    dom::core_installed_state::installed_state_clear(state);
}

dsk_status_t dsk_installed_state_parse(const dsk_u8* data,
                                       dsk_u32 size,
                                       dsk_installed_state_t* out_state) {
    err_t err = dom::core_installed_state::installed_state_parse(
        (const unsigned char*)data,
        (u32)size,
        out_state);
    return dsk_state_map_err(&err);
}

dsk_status_t dsk_installed_state_write(const dsk_installed_state_t* state,
                                       dsk_tlv_buffer_t* out_buf) {
    err_t err = dom::core_installed_state::installed_state_write(state, out_buf);
    return dsk_state_map_err(&err);
}
