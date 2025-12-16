/*
FILE: source/dominium/launcher/core/include/launcher_tlv.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tlv
RESPONSIBILITY: Versioned TLV encode/decode helpers for launcher core persistence; deterministic, skip-unknown, forward-compatible.
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types only; no OS/UI/toolkit headers.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Encodes integers in little-endian; does not depend on host endianness or pointer identity.
VERSIONING / ABI / DATA FORMAT NOTES: TLV is `{u32 tag, u32 len, u8[len] payload}` repeated; root contains an explicit schema version tag.
EXTENSION POINTS: New tags may be added; unknown tags must be skipped.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_H

#include <stddef.h>
#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace launcher_core {

/* Canonical TLV record header size (tag + len). */
enum { LAUNCHER_TLV_HEADER_BYTES = 8u };

/* Root schema version tag (must appear at most once per root). */
enum { LAUNCHER_TLV_TAG_SCHEMA_VERSION = 1u };

struct TlvRecord {
    u32 tag;
    const unsigned char* payload;
    u32 len;
};

class TlvReader {
public:
    TlvReader(const unsigned char* data, size_t size);

    /* Returns false when no more records or on malformed input. */
    bool next(TlvRecord& out);

    size_t offset() const;
    size_t remaining() const;

private:
    const unsigned char* m_data;
    size_t m_size;
    size_t m_off;
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

/* Deterministic 64-bit FNV-1a over bytes (used for manifest hashing). */
u64 tlv_fnv1a64(const unsigned char* data, size_t len);

/* Little-endian helpers (TLV canonical byte order). */
void tlv_write_u32_le(unsigned char out[4], u32 v);
void tlv_write_u64_le(unsigned char out[8], u64 v);
bool tlv_read_u32_le(const unsigned char* data, u32 len, u32& out_v);
bool tlv_read_i32_le(const unsigned char* data, u32 len, i32& out_v);
bool tlv_read_u64_le(const unsigned char* data, u32 len, u64& out_v);

/* String payload is treated as raw bytes (UTF-8 recommended); no terminator required. */
std::string tlv_read_string(const unsigned char* data, u32 len);

/* Version gate helper.
 * Returns true if a supported version was read (or defaulted to 1 when absent).
 */
bool tlv_read_schema_version_or_default(const unsigned char* data,
                                        size_t size,
                                        u32& out_version,
                                        u32 default_version);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_H */

