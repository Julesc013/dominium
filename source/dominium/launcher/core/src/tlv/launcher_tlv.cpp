/*
FILE: source/dominium/launcher/core/src/tlv/launcher_tlv.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tlv
RESPONSIBILITY: Implements deterministic TLV encode/decode helpers (little-endian canonical encoding).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types only.
FORBIDDEN DEPENDENCIES: OS/UI/toolkit headers.
*/

#include "launcher_tlv.h"

#include <cstring>

namespace dom {
namespace launcher_core {

static u32 tlv__read_u32_le_unsafe(const unsigned char* p) {
    return (u32)p[0] | ((u32)p[1] << 8u) | ((u32)p[2] << 16u) | ((u32)p[3] << 24u);
}

static u64 tlv__read_u64_le_unsafe(const unsigned char* p) {
    u64 lo = (u64)tlv__read_u32_le_unsafe(p);
    u64 hi = (u64)tlv__read_u32_le_unsafe(p + 4);
    return lo | (hi << 32u);
}

TlvReader::TlvReader(const unsigned char* data, size_t size)
    : m_data(data), m_size(size), m_off(0u) {
}

bool TlvReader::next(TlvRecord& out) {
    u32 tag;
    u32 len;

    if (!m_data) {
        return false;
    }
    if (m_off + (size_t)LAUNCHER_TLV_HEADER_BYTES > m_size) {
        return false;
    }

    tag = tlv__read_u32_le_unsafe(m_data + m_off);
    len = tlv__read_u32_le_unsafe(m_data + m_off + 4u);
    m_off += (size_t)LAUNCHER_TLV_HEADER_BYTES;

    if (m_off + (size_t)len > m_size) {
        return false;
    }

    out.tag = tag;
    out.len = len;
    out.payload = (len > 0u) ? (m_data + m_off) : (const unsigned char*)0;
    m_off += (size_t)len;
    return true;
}

size_t TlvReader::offset() const { return m_off; }
size_t TlvReader::remaining() const { return (m_off <= m_size) ? (m_size - m_off) : 0u; }

TlvWriter::TlvWriter() : m_bytes() {}

void TlvWriter::reset() { m_bytes.clear(); }
const std::vector<unsigned char>& TlvWriter::bytes() const { return m_bytes; }

void tlv_write_u32_le(unsigned char out[4], u32 v) {
    out[0] = (unsigned char)(v & 0xFFu);
    out[1] = (unsigned char)((v >> 8u) & 0xFFu);
    out[2] = (unsigned char)((v >> 16u) & 0xFFu);
    out[3] = (unsigned char)((v >> 24u) & 0xFFu);
}

void tlv_write_u64_le(unsigned char out[8], u64 v) {
    tlv_write_u32_le(out, (u32)(v & 0xFFFFFFFFull));
    tlv_write_u32_le(out + 4, (u32)((v >> 32u) & 0xFFFFFFFFull));
}

bool tlv_read_u32_le(const unsigned char* data, u32 len, u32& out_v) {
    if (!data || len < 4u) {
        return false;
    }
    out_v = tlv__read_u32_le_unsafe(data);
    return true;
}

bool tlv_read_i32_le(const unsigned char* data, u32 len, i32& out_v) {
    u32 tmp;
    if (!tlv_read_u32_le(data, len, tmp)) {
        return false;
    }
    out_v = (i32)tmp;
    return true;
}

bool tlv_read_u64_le(const unsigned char* data, u32 len, u64& out_v) {
    if (!data || len < 8u) {
        return false;
    }
    out_v = tlv__read_u64_le_unsafe(data);
    return true;
}

std::string tlv_read_string(const unsigned char* data, u32 len) {
    if (!data || len == 0u) {
        return std::string();
    }
    return std::string((const char*)data, (const char*)data + (size_t)len);
}

void TlvWriter::add_bytes(u32 tag, const unsigned char* data, u32 len) {
    size_t base = m_bytes.size();
    unsigned char hdr[8];
    tlv_write_u32_le(&hdr[0], tag);
    tlv_write_u32_le(&hdr[4], len);
    m_bytes.resize(base + 8u + (size_t)len);
    std::memcpy(&m_bytes[base], hdr, 8u);
    if (len > 0u && data) {
        std::memcpy(&m_bytes[base + 8u], data, (size_t)len);
    }
}

void TlvWriter::add_u32(u32 tag, u32 value) {
    unsigned char buf[4];
    tlv_write_u32_le(buf, value);
    add_bytes(tag, buf, 4u);
}

void TlvWriter::add_i32(u32 tag, i32 value) {
    unsigned char buf[4];
    tlv_write_u32_le(buf, (u32)value);
    add_bytes(tag, buf, 4u);
}

void TlvWriter::add_u64(u32 tag, u64 value) {
    unsigned char buf[8];
    tlv_write_u64_le(buf, value);
    add_bytes(tag, buf, 8u);
}

void TlvWriter::add_string(u32 tag, const std::string& value) {
    if (value.empty()) {
        add_bytes(tag, (const unsigned char*)0, 0u);
        return;
    }
    add_bytes(tag, (const unsigned char*)value.data(), (u32)value.size());
}

void TlvWriter::add_container(u32 tag, const std::vector<unsigned char>& payload_tlv) {
    if (payload_tlv.empty()) {
        add_bytes(tag, (const unsigned char*)0, 0u);
        return;
    }
    add_bytes(tag, &payload_tlv[0], (u32)payload_tlv.size());
}

u64 tlv_fnv1a64(const unsigned char* data, size_t len) {
    const u64 FNV_OFFSET = 1469598103934665603ull;
    const u64 FNV_PRIME  = 1099511628211ull;
    u64 h = FNV_OFFSET;
    size_t i;
    if (len == 0u) {
        return FNV_OFFSET;
    }
    if (!data) {
        return 0ull;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= FNV_PRIME;
    }
    return h;
}

bool tlv_read_schema_version_or_default(const unsigned char* data,
                                        size_t size,
                                        u32& out_version,
                                        u32 default_version) {
    TlvReader r(data, size);
    TlvRecord rec;
    out_version = default_version;
    while (r.next(rec)) {
        if (rec.tag == (u32)LAUNCHER_TLV_TAG_SCHEMA_VERSION) {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                out_version = v;
                return true;
            }
            return false;
        }
    }
    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
