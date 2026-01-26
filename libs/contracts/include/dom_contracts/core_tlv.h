/*
FILE: include/dominium/core_tlv.h
MODULE: Dominium
PURPOSE: Shared TLV helpers (stream + framed).
*/
#ifndef DOMINIUM_CORE_TLV_H
#define DOMINIUM_CORE_TLV_H

#include <stddef.h>

extern "C" {
#include "domino/core/types.h"
}

#include "dom_contracts/core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Framed TLV (header + u16 tag, CRC32).
 *------------------------------------------------------------*/
#define CORE_TLV_FRAMED_MAGIC "DSK1"
#define CORE_TLV_FRAMED_MAGIC_LEN 4u
#define CORE_TLV_FRAMED_VERSION 1u
#define CORE_TLV_FRAMED_ENDIAN_LITTLE 0xFFFEu
#define CORE_TLV_FRAMED_HEADER_SIZE 20u
#define CORE_TLV_FRAMED_MAX_PAYLOAD (64u * 1024u * 1024u)

typedef enum core_tlv_subcode_e {
    CORE_TLV_SUBCODE_NONE = 0u,
    CORE_TLV_SUBCODE_TLV_BAD_MAGIC = 1u,
    CORE_TLV_SUBCODE_TLV_BAD_ENDIAN = 2u,
    CORE_TLV_SUBCODE_TLV_BAD_HEADER_SIZE = 3u,
    CORE_TLV_SUBCODE_TLV_BAD_PAYLOAD_SIZE = 4u,
    CORE_TLV_SUBCODE_TLV_BAD_CRC = 5u,
    CORE_TLV_SUBCODE_TLV_TRUNCATED = 6u,
    CORE_TLV_SUBCODE_MISSING_FIELD = 7u,
    CORE_TLV_SUBCODE_INVALID_FIELD = 8u
} core_tlv_subcode;

typedef struct core_tlv_framed_header_t {
    char magic[4];
    u16 version;
    u16 endian;
    u32 header_size;
    u32 payload_size;
    u32 header_crc;
} core_tlv_framed_header_t;

typedef struct core_tlv_framed_record_t {
    u16 type;
    const unsigned char* payload;
    u32 length;
} core_tlv_framed_record_t;

typedef struct core_tlv_framed_view_t {
    core_tlv_framed_header_t header;
    const unsigned char* payload;
    u32 payload_size;
    core_tlv_framed_record_t* records;
    u32 record_count;
} core_tlv_framed_view_t;

typedef struct core_tlv_framed_stream_t {
    const unsigned char* payload;
    u32 payload_size;
    core_tlv_framed_record_t* records;
    u32 record_count;
} core_tlv_framed_stream_t;

typedef struct core_tlv_framed_buffer_t {
    unsigned char* data;
    u32 size;
} core_tlv_framed_buffer_t;

typedef struct core_tlv_framed_builder_t core_tlv_framed_builder_t;

err_t core_tlv_framed_parse(const unsigned char* data,
                            u32 size,
                            core_tlv_framed_view_t* out_view);
void core_tlv_framed_view_destroy(core_tlv_framed_view_t* view);

err_t core_tlv_framed_parse_stream(const unsigned char* payload,
                                   u32 size,
                                   core_tlv_framed_stream_t* out_stream);
void core_tlv_framed_stream_destroy(core_tlv_framed_stream_t* stream);

const core_tlv_framed_record_t* core_tlv_framed_find_first(const core_tlv_framed_record_t* records,
                                                           u32 count,
                                                           u16 type);

core_tlv_framed_builder_t* core_tlv_framed_builder_create(void);
void core_tlv_framed_builder_destroy(core_tlv_framed_builder_t* builder);
err_t core_tlv_framed_builder_add_bytes(core_tlv_framed_builder_t* builder,
                                        u16 type,
                                        const unsigned char* payload,
                                        u32 length);
err_t core_tlv_framed_builder_add_string(core_tlv_framed_builder_t* builder,
                                         u16 type,
                                         const char* value);
err_t core_tlv_framed_builder_add_u16(core_tlv_framed_builder_t* builder,
                                      u16 type,
                                      u16 value);
err_t core_tlv_framed_builder_add_u32(core_tlv_framed_builder_t* builder,
                                      u16 type,
                                      u32 value);
err_t core_tlv_framed_builder_add_u64(core_tlv_framed_builder_t* builder,
                                      u16 type,
                                      u64 value);
err_t core_tlv_framed_builder_add_container(core_tlv_framed_builder_t* builder,
                                            u16 type,
                                            const unsigned char* payload,
                                            u32 length);

err_t core_tlv_framed_builder_finalize(const core_tlv_framed_builder_t* builder,
                                       core_tlv_framed_buffer_t* out_buf);
err_t core_tlv_framed_builder_finalize_payload(const core_tlv_framed_builder_t* builder,
                                               core_tlv_framed_buffer_t* out_buf);
void core_tlv_framed_buffer_free(core_tlv_framed_buffer_t* buf);

u32 core_tlv_crc32(const unsigned char* data, u32 size);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_TLV_H */
