#ifndef DSK_TLV_H
#define DSK_TLV_H

#include "dsk_error.h"
#include "dominium/core_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DSK_TLV_MAGIC CORE_TLV_FRAMED_MAGIC
#define DSK_TLV_MAGIC_LEN CORE_TLV_FRAMED_MAGIC_LEN
#define DSK_TLV_VERSION CORE_TLV_FRAMED_VERSION
#define DSK_TLV_ENDIAN_LITTLE CORE_TLV_FRAMED_ENDIAN_LITTLE
#define DSK_TLV_HEADER_SIZE CORE_TLV_FRAMED_HEADER_SIZE

typedef core_tlv_framed_header_t dsk_tlv_header_t;
typedef core_tlv_framed_record_t dsk_tlv_record_t;
typedef core_tlv_framed_view_t dsk_tlv_view_t;
typedef core_tlv_framed_stream_t dsk_tlv_stream_t;
typedef core_tlv_framed_buffer_t dsk_tlv_buffer_t;
typedef core_tlv_framed_builder_t dsk_tlv_builder_t;

DSK_API dsk_status_t dsk_tlv_parse(const dsk_u8 *data,
                                   dsk_u32 size,
                                   dsk_tlv_view_t *out_view);
DSK_API void dsk_tlv_view_destroy(dsk_tlv_view_t *view);

DSK_API dsk_status_t dsk_tlv_parse_stream(const dsk_u8 *payload,
                                          dsk_u32 size,
                                          dsk_tlv_stream_t *out_stream);
DSK_API void dsk_tlv_stream_destroy(dsk_tlv_stream_t *stream);

DSK_API const dsk_tlv_record_t *dsk_tlv_find_first(const dsk_tlv_record_t *records,
                                                   dsk_u32 count,
                                                   dsk_u16 type);

DSK_API dsk_tlv_builder_t *dsk_tlv_builder_create(void);
DSK_API void dsk_tlv_builder_destroy(dsk_tlv_builder_t *builder);
DSK_API dsk_status_t dsk_tlv_builder_add_bytes(dsk_tlv_builder_t *builder,
                                               dsk_u16 type,
                                               const dsk_u8 *payload,
                                               dsk_u32 length);
DSK_API dsk_status_t dsk_tlv_builder_add_string(dsk_tlv_builder_t *builder,
                                                dsk_u16 type,
                                                const char *value);
DSK_API dsk_status_t dsk_tlv_builder_add_u16(dsk_tlv_builder_t *builder,
                                             dsk_u16 type,
                                             dsk_u16 value);
DSK_API dsk_status_t dsk_tlv_builder_add_u32(dsk_tlv_builder_t *builder,
                                             dsk_u16 type,
                                             dsk_u32 value);
DSK_API dsk_status_t dsk_tlv_builder_add_u64(dsk_tlv_builder_t *builder,
                                             dsk_u16 type,
                                             dsk_u64 value);
DSK_API dsk_status_t dsk_tlv_builder_add_container(dsk_tlv_builder_t *builder,
                                                   dsk_u16 type,
                                                   const dsk_u8 *payload,
                                                   dsk_u32 length);

DSK_API dsk_status_t dsk_tlv_builder_finalize(const dsk_tlv_builder_t *builder,
                                              dsk_tlv_buffer_t *out_buf);
DSK_API dsk_status_t dsk_tlv_builder_finalize_payload(const dsk_tlv_builder_t *builder,
                                                      dsk_tlv_buffer_t *out_buf);
DSK_API void dsk_tlv_buffer_free(dsk_tlv_buffer_t *buf);

DSK_API dsk_u32 dsk_tlv_crc32(const dsk_u8 *data, dsk_u32 size);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSK_TLV_H */
