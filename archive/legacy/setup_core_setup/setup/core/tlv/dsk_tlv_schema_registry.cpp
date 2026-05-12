#include "dsk/dsk_tlv_schema_registry.h"

extern "C" {
#include "dominium/core_tlv_schema.h"
}

#include "dsk/dsk_contracts.h"
#include "dsk/dsk_tlv.h"

#include <string.h>

static err_t dsk_tlv_err_invalid_args(void) {
    return err_make((u16)ERRD_COMMON,
                    (u16)ERRC_COMMON_INVALID_ARGS,
                    (u32)ERRF_FATAL,
                    (u32)ERRMSG_COMMON_INVALID_ARGS);
}

static err_t dsk_tlv_err_parse(void) {
    return err_make((u16)ERRD_TLV,
                    (u16)ERRC_TLV_PARSE_FAILED,
                    (u32)ERRF_INTEGRITY,
                    (u32)ERRMSG_TLV_PARSE_FAILED);
}

static err_t dsk_tlv_err_integrity(void) {
    return err_make((u16)ERRD_TLV,
                    (u16)ERRC_TLV_INTEGRITY,
                    (u32)ERRF_INTEGRITY,
                    (u32)ERRMSG_TLV_INTEGRITY);
}

static err_t dsk_tlv_err_schema(u32 version) {
    err_t err = err_make((u16)ERRD_TLV,
                         (u16)ERRC_TLV_SCHEMA_VERSION,
                         (u32)(ERRF_POLICY_REFUSAL | ERRF_NOT_SUPPORTED),
                         (u32)ERRMSG_TLV_SCHEMA_VERSION);
    err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SCHEMA_VERSION, version);
    return err;
}

static u32 dsk_read_u16_le(const dsk_u8* p) {
    return (u32)p[0] | ((u32)p[1] << 8u);
}

static u32 dsk_peek_version(const dsk_u8* data, dsk_u32 size) {
    if (!data || size < 6u) {
        return 0u;
    }
    if (memcmp(data, DSK_TLV_MAGIC, DSK_TLV_MAGIC_LEN) != 0) {
        return 0u;
    }
    return dsk_read_u16_le(data + 4u);
}

static err_t dsk_status_to_err(dsk_status_t st, const dsk_u8* data, dsk_u32 size) {
    if (dsk_error_is_ok(st)) {
        return err_ok();
    }
    if (st.code == DSK_CODE_UNSUPPORTED_VERSION) {
        u32 version = dsk_peek_version(data, size);
        return dsk_tlv_err_schema(version ? version : (u32)DSK_TLV_VERSION);
    }
    if (st.code == DSK_CODE_VALIDATION_ERROR) {
        return dsk_tlv_err_integrity();
    }
    if (st.code == DSK_CODE_PARSE_ERROR || st.code == DSK_CODE_INTEGRITY_ERROR) {
        return dsk_tlv_err_parse();
    }
    return dsk_tlv_err_parse();
}

static err_t dsk_tlv_write_bytes(const core_tlv_schema_sink* sink,
                                 const unsigned char* data,
                                 u32 size) {
    if (!sink || !sink->write) {
        return dsk_tlv_err_invalid_args();
    }
    if (size > 0u && !data) {
        return dsk_tlv_err_invalid_args();
    }
    if (size > 0u && sink->write(sink->user, data, size) != 0) {
        return err_make((u16)ERRD_COMMON,
                        (u16)ERRC_COMMON_INTERNAL,
                        (u32)ERRF_FATAL,
                        (u32)ERRMSG_COMMON_INTERNAL);
    }
    return err_ok();
}

static err_t dsk_tlv_identity_migrate(u32 from_version,
                                      u32 to_version,
                                      const unsigned char* data,
                                      u32 size,
                                      const core_tlv_schema_sink* sink) {
    if (from_version != to_version) {
        return dsk_tlv_err_schema(from_version);
    }
    return dsk_tlv_write_bytes(sink, data, size);
}

static err_t validate_installed_state(const unsigned char* data,
                                      u32 size,
                                      u32* out_version) {
    dsk_status_t st;
    dsk_installed_state_t state;
    if (!data || size == 0u || !out_version) {
        return dsk_tlv_err_invalid_args();
    }
    st = dsk_installed_state_parse(data, size, &state);
    if (!dsk_error_is_ok(st)) {
        return dsk_status_to_err(st, data, size);
    }
    *out_version = (u32)DSK_TLV_VERSION;
    return err_ok();
}

int dsk_register_tlv_schemas(void) {
    core_tlv_schema_entry entry;
    core_tlv_schema_result res;

    entry.schema_id = (u32)CORE_TLV_SCHEMA_SETUP_INSTALLED_STATE;
    entry.name = "setup.installed_state";
    entry.current_version = (u32)DSK_TLV_VERSION;
    entry.min_version = (u32)DSK_TLV_VERSION;
    entry.max_version = (u32)DSK_TLV_VERSION;
    entry.validate = validate_installed_state;
    entry.migrate = dsk_tlv_identity_migrate;

    res = core_tlv_schema_register(&entry);
    if (res == CORE_TLV_SCHEMA_OK || res == CORE_TLV_SCHEMA_ERR_CONFLICT) {
        return 1;
    }
    return 0;
}
