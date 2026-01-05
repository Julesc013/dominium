/*
FILE: source/dominium/game/runtime/dom_game_handshake.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_handshake
RESPONSIBILITY: Implements game-side handshake parsing (launcher → game).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal implementation detail only.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_handshake.h"

#include <fstream>
#include <vector>

#include "dominium/core_tlv.h"
#include "runtime/dom_io_guard.h"

namespace dom {

namespace {

static bool is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

static bool is_abs_path_string(const std::string &path) {
    if (path.empty()) {
        return false;
    }
    if (path[0] == '/' || path[0] == '\\') {
        return true;
    }
    if (path.size() >= 2u && is_alpha(path[0]) && path[1] == ':') {
        return true;
    }
    return false;
}

static bool map_path_ref_base(u32 base_tag, DomGamePathBaseKind &out_kind) {
    switch (base_tag) {
    case DOM_GAME_HANDSHAKE_PATH_REF_BASE_RUN_ROOT:
        out_kind = DOM_GAME_PATH_BASE_RUN_ROOT;
        return true;
    case DOM_GAME_HANDSHAKE_PATH_REF_BASE_HOME:
        out_kind = DOM_GAME_PATH_BASE_HOME_ROOT;
        return true;
    default:
        return false;
    }
}

static bool parse_path_ref(const unsigned char *data, u32 len, DomGamePathRef &out_ref) {
    core_tlv::TlvReader r(data, (size_t)len);
    core_tlv::TlvRecord rec;
    u32 base_tag = 0u;
    std::string rel;
    bool has_base = false;
    bool has_rel = false;

    while (r.next(rec)) {
        switch (rec.tag) {
        case DOM_GAME_HANDSHAKE_PATH_REF_TAG_BASE:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, base_tag)) {
                has_base = true;
            }
            break;
        case DOM_GAME_HANDSHAKE_PATH_REF_TAG_REL:
            rel = core_tlv::tlv_read_string(rec.payload, rec.len);
            has_rel = !rel.empty();
            break;
        default:
            break;
        }
    }

    if (!has_base || !has_rel || is_abs_path_string(rel)) {
        return false;
    }

    if (!map_path_ref_base(base_tag, out_ref.base_kind)) {
        return false;
    }
    out_ref.rel = rel;
    out_ref.has_value = true;
    return true;
}

static bool read_file_bytes(const std::string &path, std::vector<unsigned char> &out) {
    if (!dom_io_guard_io_allowed()) {
        dom_io_guard_note_violation("handshake_read", path.c_str());
        return false;
    }
    std::ifstream in(path.c_str(), std::ios::binary);
    if (!in) {
        return false;
    }
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    in.seekg(0, std::ios::beg);
    if (size <= 0) {
        return false;
    }
    out.resize((size_t)size);
    in.read(reinterpret_cast<char *>(&out[0]), size);
    return in.good() || in.eof();
}

} // namespace

DomGamePathRef::DomGamePathRef()
    : base_kind(DOM_GAME_PATH_BASE_RUN_ROOT),
      rel(),
      has_value(false) {
}

DomGameHandshake::DomGameHandshake()
    : schema_version(DOM_GAME_HANDSHAKE_TLV_VERSION),
      run_id(0ull),
      instance_id(),
      instance_manifest_hash_bytes(),
      run_root_ref(),
      instance_root_ref() {
}

bool dom_game_handshake_from_tlv_bytes(const unsigned char *data,
                                       size_t size,
                                       DomGameHandshake &out_hs) {
    core_tlv::TlvReader r(data, size);
    core_tlv::TlvRecord rec;
    u32 version = 0u;

    out_hs = DomGameHandshake();
    if (!core_tlv::tlv_read_schema_version_or_default(data, size, version,
                                                      DOM_GAME_HANDSHAKE_TLV_VERSION)) {
        return false;
    }
    if (version != DOM_GAME_HANDSHAKE_TLV_VERSION) {
        return false;
    }
    out_hs.schema_version = version;

    while (r.next(rec)) {
        switch (rec.tag) {
        case core_tlv::CORE_TLV_TAG_SCHEMA_VERSION:
            break;
        case DOM_GAME_HANDSHAKE_TLV_TAG_RUN_ID: {
            u64 v = 0ull;
            if (core_tlv::tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_hs.run_id = v;
            }
            break;
        }
        case DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_ID:
            out_hs.instance_id = core_tlv::tlv_read_string(rec.payload, rec.len);
            break;
        case DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH:
            out_hs.instance_manifest_hash_bytes.assign(rec.payload, rec.payload + rec.len);
            break;
        case DOM_GAME_HANDSHAKE_TLV_TAG_RUN_ROOT_REF:
            if (!parse_path_ref(rec.payload, rec.len, out_hs.run_root_ref)) {
                return false;
            }
            break;
        case DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_ROOT_REF:
            if (!parse_path_ref(rec.payload, rec.len, out_hs.instance_root_ref)) {
                return false;
            }
            break;
        default:
            break;
        }
    }

    if (out_hs.run_id == 0ull || out_hs.instance_id.empty()) {
        return false;
    }
    return true;
}

bool dom_game_handshake_from_file(const std::string &path,
                                  DomGameHandshake &out_hs) {
    std::vector<unsigned char> bytes;
    if (path.empty()) {
        return false;
    }
    if (!read_file_bytes(path, bytes)) {
        return false;
    }
    return dom_game_handshake_from_tlv_bytes(bytes.empty() ? (const unsigned char *)0 : &bytes[0],
                                             bytes.size(),
                                             out_hs);
}

} // namespace dom
