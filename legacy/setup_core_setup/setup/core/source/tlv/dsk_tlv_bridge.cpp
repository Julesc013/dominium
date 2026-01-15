#include "dsk/dsk_tlv.h"

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

static dsk_status_t dsk_map_core_tlv_err(const err_t* err) {
    dsk_u16 subcode = dsk_subcode_from_err(err);
    if (!err || err_is_ok(err)) {
        return err_ok();
    }
    if (err->domain == (u16)ERRD_TLV) {
        if (err->code == (u16)ERRC_TLV_SCHEMA_VERSION) {
            return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_UNSUPPORTED_VERSION, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        if (err->code == (u16)ERRC_TLV_INTEGRITY) {
            return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INTEGRITY_ERROR, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_PARSE_ERROR, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
    }
    if (err->domain == (u16)ERRD_COMMON && err->code == (u16)ERRC_COMMON_INVALID_ARGS) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
    }
    return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INTERNAL_ERROR, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

dsk_status_t dsk_tlv_parse(const dsk_u8* data,
                           dsk_u32 size,
                           dsk_tlv_view_t* out_view) {
    err_t err = core_tlv_framed_parse((const unsigned char*)data, (u32)size, out_view);
    return dsk_map_core_tlv_err(&err);
}

void dsk_tlv_view_destroy(dsk_tlv_view_t* view) {
    core_tlv_framed_view_destroy(view);
}

dsk_status_t dsk_tlv_parse_stream(const dsk_u8* payload,
                                  dsk_u32 size,
                                  dsk_tlv_stream_t* out_stream) {
    err_t err = core_tlv_framed_parse_stream((const unsigned char*)payload, (u32)size, out_stream);
    return dsk_map_core_tlv_err(&err);
}

void dsk_tlv_stream_destroy(dsk_tlv_stream_t* stream) {
    core_tlv_framed_stream_destroy(stream);
}

const dsk_tlv_record_t* dsk_tlv_find_first(const dsk_tlv_record_t* records,
                                           dsk_u32 count,
                                           dsk_u16 type) {
    return core_tlv_framed_find_first(records, (u32)count, (u16)type);
}

dsk_tlv_builder_t* dsk_tlv_builder_create(void) {
    return core_tlv_framed_builder_create();
}

void dsk_tlv_builder_destroy(dsk_tlv_builder_t* builder) {
    core_tlv_framed_builder_destroy(builder);
}

dsk_status_t dsk_tlv_builder_add_bytes(dsk_tlv_builder_t* builder,
                                       dsk_u16 type,
                                       const dsk_u8* payload,
                                       dsk_u32 length) {
    err_t err = core_tlv_framed_builder_add_bytes(builder,
                                                  (u16)type,
                                                  (const unsigned char*)payload,
                                                  (u32)length);
    return dsk_map_core_tlv_err(&err);
}

dsk_status_t dsk_tlv_builder_add_string(dsk_tlv_builder_t* builder,
                                        dsk_u16 type,
                                        const char* value) {
    err_t err = core_tlv_framed_builder_add_string(builder, (u16)type, value);
    return dsk_map_core_tlv_err(&err);
}

dsk_status_t dsk_tlv_builder_add_u16(dsk_tlv_builder_t* builder,
                                     dsk_u16 type,
                                     dsk_u16 value) {
    err_t err = core_tlv_framed_builder_add_u16(builder, (u16)type, (u16)value);
    return dsk_map_core_tlv_err(&err);
}

dsk_status_t dsk_tlv_builder_add_u32(dsk_tlv_builder_t* builder,
                                     dsk_u16 type,
                                     dsk_u32 value) {
    err_t err = core_tlv_framed_builder_add_u32(builder, (u16)type, (u32)value);
    return dsk_map_core_tlv_err(&err);
}

dsk_status_t dsk_tlv_builder_add_u64(dsk_tlv_builder_t* builder,
                                     dsk_u16 type,
                                     dsk_u64 value) {
    err_t err = core_tlv_framed_builder_add_u64(builder, (u16)type, (u64)value);
    return dsk_map_core_tlv_err(&err);
}

dsk_status_t dsk_tlv_builder_add_container(dsk_tlv_builder_t* builder,
                                           dsk_u16 type,
                                           const dsk_u8* payload,
                                           dsk_u32 length) {
    err_t err = core_tlv_framed_builder_add_container(builder,
                                                      (u16)type,
                                                      (const unsigned char*)payload,
                                                      (u32)length);
    return dsk_map_core_tlv_err(&err);
}

dsk_status_t dsk_tlv_builder_finalize(const dsk_tlv_builder_t* builder,
                                      dsk_tlv_buffer_t* out_buf) {
    err_t err = core_tlv_framed_builder_finalize(builder, out_buf);
    return dsk_map_core_tlv_err(&err);
}

dsk_status_t dsk_tlv_builder_finalize_payload(const dsk_tlv_builder_t* builder,
                                              dsk_tlv_buffer_t* out_buf) {
    err_t err = core_tlv_framed_builder_finalize_payload(builder, out_buf);
    return dsk_map_core_tlv_err(&err);
}

void dsk_tlv_buffer_free(dsk_tlv_buffer_t* buf) {
    core_tlv_framed_buffer_free(buf);
}

dsk_u32 dsk_tlv_crc32(const dsk_u8* data, dsk_u32 size) {
    return (dsk_u32)core_tlv_crc32((const unsigned char*)data, (u32)size);
}
