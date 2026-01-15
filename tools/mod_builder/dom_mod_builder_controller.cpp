/*
FILE: source/dominium/tools/mod_builder/dom_mod_builder_controller.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/mod_builder/dom_mod_builder_controller
RESPONSIBILITY: Implements `dom_mod_builder_controller`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_mod_builder_controller.h"

#include <algorithm>
#include <cstdio>
#include <cstring>

#include "dominium/tools/common/dom_tool_io.h"
#include "dominium/tools/common/dom_tool_tlv.h"
#include "dominium/tools/common/dom_tool_validate.h"

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

static void append_u32(std::vector<unsigned char> &out, u32 v) {
    const size_t base = out.size();
    out.resize(base + 4u);
    std::memcpy(&out[base], &v, 4u);
}

static void append_u64(std::vector<unsigned char> &out, unsigned long long v) {
    const size_t base = out.size();
    out.resize(base + 8u);
    std::memcpy(&out[base], &v, 8u);
}

static void append_bytes(std::vector<unsigned char> &out, const unsigned char *data, size_t len) {
    if (len == 0u) return;
    const size_t base = out.size();
    out.resize(base + len);
    if (data) {
        std::memcpy(&out[base], data, len);
    }
}

struct Entry {
    std::string name;
    std::vector<unsigned char> data;
};

static bool entry_less(const Entry &a, const Entry &b) {
    return a.name < b.name;
}

static void build_index_txt(const std::vector<Entry> &entries, std::vector<unsigned char> &out) {
    std::string s;
    size_t i;
    s = "DMOD index (deterministic)\n";
    for (i = 0u; i < entries.size(); ++i) {
        char line[256];
        std::sprintf(line, "%s,%u\n", entries[i].name.c_str(), (unsigned)entries[i].data.size());
        s.append(line);
    }
    out.resize(s.size());
    if (!s.empty()) {
        std::memcpy(&out[0], s.c_str(), s.size());
    }
}

} // namespace

DomModBuilderController::DomModBuilderController()
    : m_file_bytes(),
      m_content_stream(),
      m_canonical_content_stream(),
      m_canonical_manifest(),
      m_mod_id(0u),
      m_mod_version(0u),
      m_mod_name(),
      m_record_count(0u) {}

const char *DomModBuilderController::tool_id() const { return "mod_builder"; }
const char *DomModBuilderController::tool_name() const { return "Mod Builder"; }
const char *DomModBuilderController::tool_description() const { return "Build deterministic .dmod packages from TLV manifests."; }

bool DomModBuilderController::supports_demo() const { return true; }

std::string DomModBuilderController::demo_path(const std::string &home) const {
    return join_slash(home, "data/tools_demo/mod_demo.tlv");
}

bool DomModBuilderController::extract_kv_tag_payload(const std::vector<unsigned char> &kv_payload,
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

bool DomModBuilderController::canonicalize_kv_payload(const std::vector<unsigned char> &in,
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

bool DomModBuilderController::canonicalize_record_stream(const std::vector<unsigned char> &in,
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

unsigned long long DomModBuilderController::fnv1a64(const unsigned char *data, size_t len) {
    unsigned long long h = 14695981039346656037ULL;
    size_t i;
    for (i = 0u; i < len; ++i) {
        h ^= (unsigned long long)(data ? data[i] : 0u);
        h *= 1099511628211ULL;
    }
    return h;
}

bool DomModBuilderController::read_u32_field(const std::vector<unsigned char> &kv_payload, u32 tag, u32 &out) {
    d_tlv_blob blob;
    u32 off = 0u;
    u32 cur = 0u;
    d_tlv_blob payload;
    blob.ptr = kv_payload.empty() ? (unsigned char *)0 : (unsigned char *)&kv_payload[0];
    blob.len = (u32)kv_payload.size();
    while (1) {
        const int rc = tlv_next(&blob, &off, &cur, &payload);
        if (rc == 1) break;
        if (rc != 0) return false;
        if (cur == tag && payload.len == 4u && payload.ptr) {
            out = read_u32(payload.ptr);
            return true;
        }
    }
    return false;
}

bool DomModBuilderController::read_string_field(const std::vector<unsigned char> &kv_payload, u32 tag, std::string &out) {
    d_tlv_blob blob;
    u32 off = 0u;
    u32 cur = 0u;
    d_tlv_blob payload;
    blob.ptr = kv_payload.empty() ? (unsigned char *)0 : (unsigned char *)&kv_payload[0];
    blob.len = (u32)kv_payload.size();
    while (1) {
        const int rc = tlv_next(&blob, &off, &cur, &payload);
        if (rc == 1) break;
        if (rc != 0) return false;
        if (cur == tag && payload.len > 0u && payload.ptr) {
            const char *s = (const char *)payload.ptr;
            size_t n = 0u;
            while (n < (size_t)payload.len && s[n] != '\0') {
                ++n;
            }
            out.assign(s, n);
            return true;
        }
    }
    return false;
}

std::string DomModBuilderController::dirname_of(const std::string &path) {
    size_t i;
    if (path.empty()) return std::string();
    for (i = path.size(); i > 0u; --i) {
        const char c = path[i - 1u];
        if (c == '/' || c == '\\') {
            return path.substr(0u, i - 1u);
        }
    }
    return std::string();
}

std::string DomModBuilderController::join_slash(const std::string &a, const std::string &b) {
    if (a.empty()) return b;
    if (b.empty()) return a;
    std::string out = a;
    if (out[out.size() - 1u] != '/' && out[out.size() - 1u] != '\\') {
        out.push_back('/');
    }
    out.append(b);
    return out;
}

std::string DomModBuilderController::version_u32(unsigned v) {
    char buf[32];
    std::sprintf(buf, "%08u", v);
    return std::string(buf);
}

bool DomModBuilderController::build_canonical_manifest(std::string &status) {
    std::vector<unsigned char> canon_kv;
    std::vector<unsigned char> canon_content;
    std::vector<unsigned char> tmp;
    unsigned long long hash64 = 0ULL;

    if (!canonicalize_record_stream(m_content_stream, canon_content)) {
        status = "Failed to canonicalize content stream.";
        return false;
    }

    hash64 = fnv1a64(canon_content.empty() ? (const unsigned char *)0 : &canon_content[0], canon_content.size());

    /* Rebuild KV payload deterministically, replacing CONTENT and HASH fields. */
    {
        d_tlv_blob blob;
        u32 off = 0u;
        u32 tag = 0u;
        d_tlv_blob payload;
        DomTlvKVBuilder kv;
        bool have_hash = false;

        blob.ptr = m_file_bytes.empty() ? (unsigned char *)0 : (unsigned char *)&m_file_bytes[0];
        blob.len = (u32)m_file_bytes.size();

        while (1) {
            const int rc = tlv_next(&blob, &off, &tag, &payload);
            if (rc == 1) break;
            if (rc != 0) {
                status = "Malformed mod manifest.";
                return false;
            }
            if (tag == D_FIELD_MOD_CONTENT) {
                if (!canon_content.empty()) {
                    kv.field_blob(tag, &canon_content[0], (u32)canon_content.size());
                } else {
                    kv.field_blob(tag, (const unsigned char *)0, 0u);
                }
            } else if (tag == 0x07u /* tool-added hash */) {
                have_hash = true;
                kv.field_blob(tag, (const unsigned char *)&hash64, 8u);
            } else {
                kv.field_blob(tag, payload.ptr, payload.len);
            }
        }

        /* Ensure hash field exists even if absent in input. */
        if (!have_hash) {
            kv.field_blob(0x07u, (const unsigned char *)&hash64, 8u);
        }

        canon_kv = kv.finalize();
    }

    m_canonical_content_stream.swap(canon_content);
    m_canonical_manifest.swap(canon_kv);
    return true;
}

bool DomModBuilderController::load(const std::string &path, std::string &status) {
    std::string err;
    m_file_bytes.clear();
    m_content_stream.clear();
    m_canonical_content_stream.clear();
    m_canonical_manifest.clear();
    m_mod_id = 0u;
    m_mod_version = 0u;
    m_mod_name.clear();
    m_record_count = 0u;

    if (!read_file(path, m_file_bytes, &err)) {
        status = err.empty() ? "Failed to read file." : err;
        return false;
    }

    if (!validate_schema_payload(D_TLV_SCHEMA_MOD_V1, m_file_bytes, &err)) {
        status = err.empty() ? "Not a valid MOD_V1 TLV manifest." : err;
        return false;
    }

    if (!extract_kv_tag_payload(m_file_bytes, D_FIELD_MOD_CONTENT, m_content_stream)) {
        status = "Malformed mod manifest (content field).";
        return false;
    }

    (void)read_u32_field(m_file_bytes, D_FIELD_MOD_ID, m_mod_id);
    (void)read_u32_field(m_file_bytes, D_FIELD_MOD_VERSION, m_mod_version);
    (void)read_string_field(m_file_bytes, D_FIELD_MOD_NAME, m_mod_name);

    {
        d_tlv_blob blob;
        u32 off = 0u;
        u32 schema_id = 0u;
        d_tlv_blob payload;

        blob.ptr = m_content_stream.empty() ? (unsigned char *)0 : (unsigned char *)&m_content_stream[0];
        blob.len = (u32)m_content_stream.size();
        while (1) {
            const int rc = tlv_next(&blob, &off, &schema_id, &payload);
            if (rc == 1) break;
            if (rc != 0) break;
            m_record_count += 1u;
        }
    }

    if (!build_canonical_manifest(status)) {
        return false;
    }

    status = "Loaded.";
    return true;
}

bool DomModBuilderController::validate(std::string &status) {
    std::string err;

    if (m_canonical_manifest.empty()) {
        status = "Nothing loaded.";
        return false;
    }
    if (!validate_schema_payload(D_TLV_SCHEMA_MOD_V1, m_canonical_manifest, &err)) {
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

bool DomModBuilderController::build_dmod_archive(std::vector<unsigned char> &out,
                                                std::string &status) const {
    std::vector<Entry> entries;
    Entry mod;
    Entry idx;
    std::vector<unsigned char> index_txt;
    size_t i;

    (void)status;
    out.clear();

    mod.name = "mod.tlv";
    mod.data = m_canonical_manifest;
    entries.push_back(mod);

    build_index_txt(entries, index_txt);
    idx.name = "index.txt";
    idx.data.swap(index_txt);
    entries.push_back(idx);

    std::sort(entries.begin(), entries.end(), entry_less);

    /* Header */
    out.push_back('D');
    out.push_back('M');
    out.push_back('O');
    out.push_back('D');
    append_u32(out, 1u);
    append_u32(out, (u32)entries.size());

    for (i = 0u; i < entries.size(); ++i) {
        const u32 nlen = (u32)entries[i].name.size();
        const u32 dlen = (u32)entries[i].data.size();
        append_u32(out, nlen);
        append_bytes(out, (const unsigned char *)entries[i].name.c_str(), (size_t)nlen);
        append_u32(out, dlen);
        if (dlen > 0u) {
            append_bytes(out, &entries[i].data[0], (size_t)dlen);
        }
    }

    /* Footer: content hash */
    {
        const unsigned long long h = fnv1a64(
            m_canonical_content_stream.empty() ? (const unsigned char *)0 : &m_canonical_content_stream[0],
            m_canonical_content_stream.size());
        append_u64(out, h);
    }

    return true;
}

bool DomModBuilderController::save(const std::string &path, std::string &status) {
    std::string err;
    std::vector<unsigned char> archive;
    std::string out_dir = dirname_of(path);
    std::string base = m_mod_name.empty() ? version_u32(m_mod_id) : m_mod_name;
    std::string ver = version_u32(m_mod_version);
    std::string out_name = base + "-" + ver + ".dmod";
    std::string out_path = out_dir.empty() ? out_name : join_slash(out_dir, out_name);

    if (!validate(status)) {
        return false;
    }

    if (!write_file(path,
                    m_canonical_manifest.empty() ? (const unsigned char *)0 : &m_canonical_manifest[0],
                    m_canonical_manifest.size(),
                    &err)) {
        status = err.empty() ? "Failed to write mod manifest." : err;
        return false;
    }

    if (!build_dmod_archive(archive, status)) {
        return false;
    }
    if (!write_file(out_path,
                    archive.empty() ? (const unsigned char *)0 : &archive[0],
                    archive.size(),
                    &err)) {
        status = err.empty() ? "Failed to write .dmod." : err;
        return false;
    }

    status = std::string("Built ") + out_name;
    return true;
}

void DomModBuilderController::summary(std::string &out) const {
    char buf[128];
    std::sprintf(buf, "records=%u id=%u ver=%u",
                 (unsigned)m_record_count,
                 (unsigned)m_mod_id,
                 (unsigned)m_mod_version);
    out = buf;
}

} // namespace tools
} // namespace dom
