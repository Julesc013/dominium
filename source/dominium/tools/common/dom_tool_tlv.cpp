/*
FILE: source/dominium/tools/common/dom_tool_tlv.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_tlv
RESPONSIBILITY: Implements `dom_tool_tlv`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_tlv.h"

#include <algorithm>
#include <cstring>

namespace dom {
namespace tools {
namespace {

static void append_bytes(std::vector<unsigned char> &out, const void *data, size_t len) {
    if (len == 0u) {
        return;
    }
    const size_t base = out.size();
    out.resize(base + len);
    if (data) {
        std::memcpy(&out[base], data, len);
    }
}

static void append_u32(std::vector<unsigned char> &out, u32 v) {
    append_bytes(out, &v, sizeof(u32));
}

static int bytes_less(const std::vector<unsigned char> &a, const std::vector<unsigned char> &b) {
    const size_t n = (a.size() < b.size()) ? a.size() : b.size();
    size_t i;
    for (i = 0u; i < n; ++i) {
        if (a[i] < b[i]) return 1;
        if (a[i] > b[i]) return 0;
    }
    return a.size() < b.size();
}

struct FieldLess {
    bool operator()(const DomTlvKVBuilder::Field &a, const DomTlvKVBuilder::Field &b) const {
        if (a.tag != b.tag) {
            return a.tag < b.tag;
        }
        return bytes_less(a.payload, b.payload) != 0;
    }
};

static u32 extract_u32_field_or_zero(const std::vector<unsigned char> &kv_blob, u32 wanted_tag) {
    d_tlv_blob blob;
    u32 offset = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;

    blob.ptr = kv_blob.empty() ? (unsigned char *)0 : (unsigned char *)&kv_blob[0];
    blob.len = (u32)kv_blob.size();

    while (1) {
        const int rc = tlv_next(&blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return 0u;
        }
        if (tag == wanted_tag && payload.len == 4u && payload.ptr) {
            u32 v = 0u;
            std::memcpy(&v, payload.ptr, sizeof(u32));
            return v;
        }
    }
    return 0u;
}

struct RecordLess {
    bool operator()(const DomTlvStreamBuilder::Record &a, const DomTlvStreamBuilder::Record &b) const {
        if (a.tag != b.tag) {
            return a.tag < b.tag;
        }
        if (a.sort_id != b.sort_id) {
            return a.sort_id < b.sort_id;
        }
        return bytes_less(a.payload, b.payload) != 0;
    }
};

} // namespace

int tlv_next(const d_tlv_blob *blob,
             u32 *offset,
             u32 *tag,
             d_tlv_blob *payload) {
    u32 remaining;
    u32 len;

    if (!blob || !offset || !tag || !payload) {
        return -1;
    }
    if (*offset >= blob->len) {
        return 1;
    }
    remaining = blob->len - *offset;
    if (remaining < 8u || !blob->ptr) {
        return -1;
    }

    std::memcpy(tag, blob->ptr + *offset, sizeof(u32));
    std::memcpy(&len, blob->ptr + *offset + 4u, sizeof(u32));
    *offset += 8u;

    if (len > blob->len - *offset) {
        return -1;
    }
    payload->ptr = blob->ptr + *offset;
    payload->len = len;
    *offset += len;
    return 0;
}

DomTlvKVBuilder::DomTlvKVBuilder() : m_fields() {}

void DomTlvKVBuilder::clear() {
    m_fields.clear();
}

void DomTlvKVBuilder::field_u32(u32 tag, u32 v) {
    Field f;
    f.tag = tag;
    f.payload.resize(4u);
    std::memcpy(&f.payload[0], &v, 4u);
    m_fields.push_back(f);
}

void DomTlvKVBuilder::field_u16(u32 tag, u16 v) {
    Field f;
    f.tag = tag;
    f.payload.resize(2u);
    std::memcpy(&f.payload[0], &v, 2u);
    m_fields.push_back(f);
}

void DomTlvKVBuilder::field_q16_16(u32 tag, q16_16 v) {
    const i32 tmp = (i32)v;
    Field f;
    f.tag = tag;
    f.payload.resize(4u);
    std::memcpy(&f.payload[0], &tmp, 4u);
    m_fields.push_back(f);
}

void DomTlvKVBuilder::field_q32_32(u32 tag, q32_32 v) {
    const i64 tmp = (i64)v;
    Field f;
    f.tag = tag;
    f.payload.resize(8u);
    std::memcpy(&f.payload[0], &tmp, 8u);
    m_fields.push_back(f);
}

void DomTlvKVBuilder::field_blob(u32 tag, const unsigned char *data, u32 len) {
    Field f;
    f.tag = tag;
    if (len > 0u) {
        f.payload.resize((size_t)len);
        if (data) {
            std::memcpy(&f.payload[0], data, (size_t)len);
        } else {
            f.payload.clear();
        }
    }
    m_fields.push_back(f);
}

void DomTlvKVBuilder::field_blob(u32 tag, const d_tlv_blob &blob) {
    field_blob(tag, blob.ptr, blob.len);
}

void DomTlvKVBuilder::field_string(u32 tag, const std::string &utf8) {
    Field f;
    f.tag = tag;
    f.payload.resize(utf8.size() + 1u);
    if (!utf8.empty()) {
        std::memcpy(&f.payload[0], utf8.c_str(), utf8.size());
    }
    f.payload[utf8.size()] = '\0';
    m_fields.push_back(f);
}

std::vector<unsigned char> DomTlvKVBuilder::finalize() const {
    std::vector<Field> fields = m_fields;
    std::vector<unsigned char> out;
    size_t i;

    std::sort(fields.begin(), fields.end(), FieldLess());
    for (i = 0u; i < fields.size(); ++i) {
        const u32 tag = fields[i].tag;
        const u32 len = (u32)fields[i].payload.size();
        append_u32(out, tag);
        append_u32(out, len);
        if (len > 0u) {
            append_bytes(out, &fields[i].payload[0], (size_t)len);
        }
    }

    return out;
}

DomTlvStreamBuilder::DomTlvStreamBuilder() : m_records() {}

void DomTlvStreamBuilder::clear() {
    m_records.clear();
}

void DomTlvStreamBuilder::add_record(u32 tag, const std::vector<unsigned char> &payload) {
    Record r;
    r.tag = tag;
    r.sort_id = extract_u32_field_or_zero(payload, 0x01u /* common id tag */);
    r.payload = payload;
    m_records.push_back(r);
}

void DomTlvStreamBuilder::add_record(u32 tag, const DomTlvKVBuilder &kv_payload) {
    add_record(tag, kv_payload.finalize());
}

std::vector<unsigned char> DomTlvStreamBuilder::finalize() const {
    std::vector<Record> records = m_records;
    std::vector<unsigned char> out;
    size_t i;

    std::sort(records.begin(), records.end(), RecordLess());
    for (i = 0u; i < records.size(); ++i) {
        const u32 tag = records[i].tag;
        const u32 len = (u32)records[i].payload.size();
        append_u32(out, tag);
        append_u32(out, len);
        if (len > 0u) {
            append_bytes(out, &records[i].payload[0], (size_t)len);
        }
    }
    return out;
}

} // namespace tools
} // namespace dom
