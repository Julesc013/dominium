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

#include "dominium/core_err.h"

#ifdef __cplusplus
#include <string>
#include <vector>
#endif

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

#ifdef __cplusplus

namespace dom {
namespace core_tlv {

/* Canonical TLV record header size (tag + len). */
enum { CORE_TLV_HEADER_BYTES = 8u };
/* Guardrail: refuse TLVs with unbounded record counts. */
enum { CORE_TLV_MAX_RECORDS = 65535u };
/* Root schema version tag (must appear at most once per root). */
enum { CORE_TLV_TAG_SCHEMA_VERSION = 1u };

struct TlvRecord {
    u32 tag;
    const unsigned char* payload;
    u32 len;
};

class TlvReader {
public:
    TlvReader(const unsigned char* data, size_t size);
    bool next(TlvRecord& out);
    size_t offset() const;
    size_t remaining() const;

private:
    const unsigned char* m_data;
    size_t m_size;
    size_t m_off;
    u32 m_record_count;
};

class TlvWriter {
public:
    TlvWriter();

    void reset();
    const std::vector<unsigned char>& bytes() const;

    void add_bytes(u32 tag, const unsigned char* data, u32 len);
    void add_u32(u32 tag, u32 value);
    void add_i32(u32 tag, i32 value);
    void add_u64(u32 tag, u64 value);
    void add_string(u32 tag, const std::string& value);
    void add_container(u32 tag, const std::vector<unsigned char>& payload_tlv);

private:
    std::vector<unsigned char> m_bytes;
};

u64 tlv_fnv1a64(const unsigned char* data, size_t len);

void tlv_write_u32_le(unsigned char out[4], u32 v);
void tlv_write_u64_le(unsigned char out[8], u64 v);
bool tlv_read_u32_le(const unsigned char* data, u32 len, u32& out_v);
bool tlv_read_i32_le(const unsigned char* data, u32 len, i32& out_v);
bool tlv_read_u64_le(const unsigned char* data, u32 len, u64& out_v);

std::string tlv_read_string(const unsigned char* data, u32 len);

bool tlv_read_schema_version_or_default(const unsigned char* data,
                                        size_t size,
                                        u32& out_version,
                                        u32 default_version);

} /* namespace core_tlv */
} /* namespace dom */

#endif /* __cplusplus */

#endif /* DOMINIUM_CORE_TLV_H */
