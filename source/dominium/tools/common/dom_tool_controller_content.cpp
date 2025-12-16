/*
FILE: source/dominium/tools/common/dom_tool_controller_content.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_controller_content
RESPONSIBILITY: Implements `dom_tool_controller_content`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_controller_content.h"

#include <cstdio>
#include <cstring>

#include "dom_tool_io.h"
#include "dom_tool_tlv.h"
#include "dom_tool_validate.h"

extern "C" {
#include "content/d_content_schema.h"
}

namespace dom {
namespace tools {
namespace {

static u32 read_u32(const unsigned char *p) {
    u32 v = 0u;
    if (p) {
        std::memcpy(&v, p, sizeof(u32));
    }
    return v;
}

static std::string join_path_slash(const std::string &a, const std::string &b) {
    if (a.empty()) return b;
    if (b.empty()) return a;
    std::string out = a;
    if (out[out.size() - 1u] != '/' && out[out.size() - 1u] != '\\') {
        out.push_back('/');
    }
    out.append(b);
    return out;
}

} // namespace

DomContentToolController::DomContentToolController(const char *tool_id,
                                                   const char *tool_name,
                                                   const char *tool_description,
                                                   const u32 *focus_schema_ids,
                                                   size_t focus_schema_count,
                                                   const char *demo_rel_path)
    : m_tool_id(tool_id ? tool_id : ""),
      m_tool_name(tool_name ? tool_name : ""),
      m_tool_desc(tool_description ? tool_description : ""),
      m_focus_schemas(),
      m_demo_rel_path(demo_rel_path ? demo_rel_path : ""),
      m_kind(SRC_NONE),
      m_single_schema_id(0u),
      m_file_bytes(),
      m_content_stream(),
      m_canonical_content_stream(),
      m_canonical_file_bytes(),
      m_total_records(0u),
      m_focus_records(0u) {
    size_t i;
    for (i = 0u; i < focus_schema_count; ++i) {
        m_focus_schemas.push_back(focus_schema_ids[i]);
    }
    if (!m_focus_schemas.empty()) {
        m_single_schema_id = m_focus_schemas[0];
    }
}

const char *DomContentToolController::tool_id() const { return m_tool_id.c_str(); }
const char *DomContentToolController::tool_name() const { return m_tool_name.c_str(); }
const char *DomContentToolController::tool_description() const { return m_tool_desc.c_str(); }

bool DomContentToolController::supports_demo() const {
    return !m_demo_rel_path.empty();
}

std::string DomContentToolController::demo_path(const std::string &home) const {
    if (m_demo_rel_path.empty()) {
        return std::string();
    }
    return join_path_slash(home, m_demo_rel_path);
}

bool DomContentToolController::is_focus_schema(u32 schema_id) const {
    size_t i;
    for (i = 0u; i < m_focus_schemas.size(); ++i) {
        if (m_focus_schemas[i] == schema_id) {
            return true;
        }
    }
    return false;
}

bool DomContentToolController::extract_kv_blob_tag(const std::vector<unsigned char> &kv_payload,
                                                   u32 tag,
                                                   std::vector<unsigned char> &out_payload) const {
    d_tlv_blob blob;
    u32 off = 0u;
    u32 cur = 0u;
    d_tlv_blob payload;

    out_payload.clear();
    blob.ptr = kv_payload.empty() ? (unsigned char *)0 : (unsigned char *)&kv_payload[0];
    blob.len = (u32)kv_payload.size();

    while (1) {
        const int rc = tlv_next(&blob, &off, &cur, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return false;
        }
        if (cur == tag) {
            out_payload.resize((size_t)payload.len);
            if (payload.len > 0u && payload.ptr) {
                std::memcpy(&out_payload[0], payload.ptr, (size_t)payload.len);
            }
        }
    }
    return true;
}

bool DomContentToolController::canonicalize_kv_payload(const std::vector<unsigned char> &in,
                                                       std::vector<unsigned char> &out) {
    d_tlv_blob blob;
    u32 off = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;
    DomTlvKVBuilder kv;

    blob.ptr = in.empty() ? (unsigned char *)0 : (unsigned char *)&in[0];
    blob.len = (u32)in.size();

    while (1) {
        const int rc = tlv_next(&blob, &off, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return false;
        }
        kv.field_blob(tag, payload.ptr, payload.len);
    }

    out = kv.finalize();
    return true;
}

bool DomContentToolController::canonicalize_record_stream(const std::vector<unsigned char> &in,
                                                          std::vector<unsigned char> &out) {
    d_tlv_blob blob;
    u32 off = 0u;
    u32 schema_id = 0u;
    d_tlv_blob payload;
    DomTlvStreamBuilder stream;

    blob.ptr = in.empty() ? (unsigned char *)0 : (unsigned char *)&in[0];
    blob.len = (u32)in.size();

    while (1) {
        const int rc = tlv_next(&blob, &off, &schema_id, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return false;
        }
        std::vector<unsigned char> pvec;
        std::vector<unsigned char> canon;
        pvec.resize((size_t)payload.len);
        if (payload.len > 0u && payload.ptr) {
            std::memcpy(&pvec[0], payload.ptr, (size_t)payload.len);
        }
        if (!canonicalize_kv_payload(pvec, canon)) {
            return false;
        }
        stream.add_record(schema_id, canon);
    }

    out = stream.finalize();
    return true;
}

bool DomContentToolController::canonicalize_kv_payload_replace_blob_tag(
    const std::vector<unsigned char> &in,
    u32 replace_tag,
    const std::vector<unsigned char> &replacement,
    std::vector<unsigned char> &out
) {
    d_tlv_blob blob;
    u32 off = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;
    DomTlvKVBuilder kv;

    blob.ptr = in.empty() ? (unsigned char *)0 : (unsigned char *)&in[0];
    blob.len = (u32)in.size();

    while (1) {
        const int rc = tlv_next(&blob, &off, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return false;
        }
        if (tag == replace_tag) {
            if (!replacement.empty()) {
                kv.field_blob(tag, &replacement[0], (u32)replacement.size());
            } else {
                kv.field_blob(tag, (const unsigned char *)0, 0u);
            }
        } else {
            kv.field_blob(tag, payload.ptr, payload.len);
        }
    }

    out = kv.finalize();
    return true;
}

bool DomContentToolController::compute_counts_and_canonicalize(std::string &status) {
    d_tlv_blob blob;
    u32 off = 0u;
    u32 schema_id = 0u;
    d_tlv_blob payload;

    m_total_records = 0u;
    m_focus_records = 0u;

    blob.ptr = m_content_stream.empty() ? (unsigned char *)0 : (unsigned char *)&m_content_stream[0];
    blob.len = (u32)m_content_stream.size();

    while (1) {
        const int rc = tlv_next(&blob, &off, &schema_id, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            status = "Malformed content stream.";
            return false;
        }
        m_total_records += 1u;
        if (is_focus_schema(schema_id)) {
            m_focus_records += 1u;
        }
    }

    if (!canonicalize_record_stream(m_content_stream, m_canonical_content_stream)) {
        status = "Failed to canonicalize content stream.";
        return false;
    }

    return true;
}

bool DomContentToolController::load(const std::string &path, std::string &status) {
    std::string err;
    m_kind = SRC_NONE;
    m_single_schema_id = m_focus_schemas.empty() ? 0u : m_focus_schemas[0];
    m_file_bytes.clear();
    m_content_stream.clear();
    m_canonical_content_stream.clear();
    m_canonical_file_bytes.clear();
    m_total_records = 0u;
    m_focus_records = 0u;

    if (!read_file(path, m_file_bytes, &err)) {
        status = err.empty() ? "Failed to read file." : err;
        return false;
    }
    if (m_file_bytes.size() < 8u) {
        m_kind = SRC_SINGLE_PAYLOAD;
        if (!canonicalize_kv_payload(m_file_bytes, m_canonical_file_bytes)) {
            status = "Failed to canonicalize payload.";
            return false;
        }
        status = "Loaded (payload).";
        return true;
    }

    {
        const u32 first_tag = read_u32(&m_file_bytes[0]);
        if (first_tag >= 0x0100u) {
            m_kind = SRC_RECORD_STREAM;
            m_content_stream = m_file_bytes;
            if (!compute_counts_and_canonicalize(status)) {
                return false;
            }
            m_canonical_file_bytes = m_canonical_content_stream;
            status = "Loaded (content stream).";
            return true;
        }
    }

    /* KV payload: try as MOD or PACK manifest; otherwise treat as single payload. */
    if (validate_schema_payload(D_TLV_SCHEMA_MOD_V1, m_file_bytes, (std::string *)0)) {
        m_kind = SRC_MOD_MANIFEST;
        if (!extract_kv_blob_tag(m_file_bytes, D_FIELD_MOD_CONTENT, m_content_stream)) {
            status = "Malformed mod manifest.";
            return false;
        }
        if (!compute_counts_and_canonicalize(status)) {
            return false;
        }
        if (!canonicalize_kv_payload_replace_blob_tag(m_file_bytes, D_FIELD_MOD_CONTENT, m_canonical_content_stream, m_canonical_file_bytes)) {
            status = "Failed to canonicalize mod manifest.";
            return false;
        }
        status = "Loaded (mod manifest).";
        return true;
    }
    if (validate_schema_payload(D_TLV_SCHEMA_PACK_V1, m_file_bytes, (std::string *)0)) {
        m_kind = SRC_PACK_MANIFEST;
        if (!extract_kv_blob_tag(m_file_bytes, D_FIELD_PACK_CONTENT, m_content_stream)) {
            status = "Malformed pack manifest.";
            return false;
        }
        if (!compute_counts_and_canonicalize(status)) {
            return false;
        }
        if (!canonicalize_kv_payload_replace_blob_tag(m_file_bytes, D_FIELD_PACK_CONTENT, m_canonical_content_stream, m_canonical_file_bytes)) {
            status = "Failed to canonicalize pack manifest.";
            return false;
        }
        status = "Loaded (pack manifest).";
        return true;
    }

    m_kind = SRC_SINGLE_PAYLOAD;
    if (!canonicalize_kv_payload(m_file_bytes, m_canonical_file_bytes)) {
        status = "Failed to canonicalize payload.";
        return false;
    }
    status = "Loaded (payload).";
    return true;
}

bool DomContentToolController::validate(std::string &status) {
    std::string err;

    if (m_kind == SRC_RECORD_STREAM) {
        if (!validate_record_stream(m_canonical_content_stream, &err)) {
            status = err.empty() ? "Schema validation failed." : err;
            return false;
        }
        if (!validate_with_engine_content(m_canonical_content_stream, &err)) {
            status = err.empty() ? "Engine validation failed." : err;
            return false;
        }
        status = "Validation OK.";
        return true;
    }
    if (m_kind == SRC_MOD_MANIFEST) {
        if (!validate_schema_payload(D_TLV_SCHEMA_MOD_V1, m_canonical_file_bytes, &err)) {
            status = err.empty() ? "Mod schema validation failed." : err;
            return false;
        }
        if (!validate_record_stream(m_canonical_content_stream, &err)) {
            status = err.empty() ? "Content schema validation failed." : err;
            return false;
        }
        if (!validate_with_engine_content(m_canonical_content_stream, &err)) {
            status = err.empty() ? "Engine validation failed." : err;
            return false;
        }
        status = "Validation OK.";
        return true;
    }
    if (m_kind == SRC_PACK_MANIFEST) {
        if (!validate_schema_payload(D_TLV_SCHEMA_PACK_V1, m_canonical_file_bytes, &err)) {
            status = err.empty() ? "Pack schema validation failed." : err;
            return false;
        }
        if (!validate_record_stream(m_canonical_content_stream, &err)) {
            status = err.empty() ? "Content schema validation failed." : err;
            return false;
        }
        if (!validate_with_engine_content(m_canonical_content_stream, &err)) {
            status = err.empty() ? "Engine validation failed." : err;
            return false;
        }
        status = "Validation OK.";
        return true;
    }
    if (m_kind == SRC_SINGLE_PAYLOAD) {
        if (m_single_schema_id != 0u) {
            if (!validate_schema_payload(m_single_schema_id, m_canonical_file_bytes, &err)) {
                status = err.empty() ? "Schema validation failed." : err;
                return false;
            }
        }
        status = "Validation OK.";
        return true;
    }

    status = "Nothing loaded.";
    return false;
}

bool DomContentToolController::save(const std::string &path, std::string &status) {
    std::string err;
    if (!validate(status)) {
        return false;
    }
    if (!write_file(path,
                    m_canonical_file_bytes.empty() ? (const unsigned char *)0 : &m_canonical_file_bytes[0],
                    m_canonical_file_bytes.size(),
                    &err)) {
        status = err.empty() ? "Write failed." : err;
        return false;
    }
    status = "Saved.";
    return true;
}

void DomContentToolController::summary(std::string &out) const {
    char buf[128];
    std::sprintf(buf, "records=%u focus=%u",
                 (unsigned)m_total_records,
                 (unsigned)m_focus_records);
    out = buf;
}

} // namespace tools
} // namespace dom

