/*
FILE: source/dominium/tools/save_inspector/dom_save_inspector_controller.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/save_inspector/dom_save_inspector_controller
RESPONSIBILITY: Implements `dom_save_inspector_controller`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_save_inspector_controller.h"

#include <cstdio>
#include <cstring>

#include "dominium/tools/common/dom_tool_io.h"

extern "C" {
#include "domino/sim/sim.h"
#include "sim/d_sim_hash.h"
#include "world/d_serialize.h"
}

namespace dom {
namespace tools {
namespace {

static bool has_dwrl_header(const std::vector<unsigned char> &data) {
    return data.size() >= 6u &&
           data[0] == 'D' && data[1] == 'W' && data[2] == 'R' && data[3] == 'L';
}

} // namespace

DomSaveInspectorController::DomSaveInspectorController()
    : m_world((d_world *)0),
      m_hash(0ULL),
      m_format("(none)") {}

DomSaveInspectorController::~DomSaveInspectorController() {
    if (m_world) {
        d_world_destroy(m_world);
        m_world = (d_world *)0;
    }
}

const char *DomSaveInspectorController::tool_id() const { return "save_inspector"; }
const char *DomSaveInspectorController::tool_name() const { return "Save Inspector"; }
const char *DomSaveInspectorController::tool_description() const { return "Inspect saves and compute world hashes."; }

bool DomSaveInspectorController::supports_demo() const { return false; }

std::string DomSaveInspectorController::demo_path(const std::string &home) const {
    (void)home;
    return std::string();
}

bool DomSaveInspectorController::load_game_save_blob(const std::vector<unsigned char> &data, std::string &status) {
    d_world_meta meta;
    d_world *w;
    u32 offset = 0u;

    std::memset(&meta, 0, sizeof(meta));
    meta.seed = 0u;
    meta.world_size_m = 0u;
    meta.vertical_min = 0;
    meta.vertical_max = 0;
    meta.core_version = 0u;
    meta.suite_version = 0u;
    meta.compat_profile_id = 0u;
    meta.extra.ptr = (unsigned char *)0;
    meta.extra.len = 0u;

    w = d_world_create(&meta);
    if (!w) {
        status = "Failed to create world.";
        return false;
    }

    while (offset + 8u <= data.size()) {
        u32 tag = 0u;
        u32 len = 0u;
        std::memcpy(&tag, &data[offset], sizeof(u32));
        std::memcpy(&len, &data[offset + 4u], sizeof(u32));
        offset += 8u;
        if (len > (u32)(data.size() - offset)) {
            d_world_destroy(w);
            status = "Truncated save blob.";
            return false;
        }

        if (tag == 1u) { /* instance */
            d_tlv_blob blob;
            blob.ptr = const_cast<unsigned char *>(&data[offset]);
            blob.len = len;
            if (d_serialize_load_instance_all(w, &blob) != 0) {
                d_world_destroy(w);
                status = "Instance load failed.";
                return false;
            }
        } else if (tag == 2u) { /* chunk */
            const size_t meta_size = sizeof(i32) + sizeof(i32) + sizeof(u32) + sizeof(u32);
            i32 cx = 0;
            i32 cy = 0;
            u32 chunk_id = 0u;
            u32 flags = 0u;
            d_chunk *chunk;
            d_tlv_blob chunk_blob;

            if ((size_t)len < meta_size) {
                d_world_destroy(w);
                status = "Chunk payload truncated.";
                return false;
            }
            std::memcpy(&cx, &data[offset], sizeof(i32));
            std::memcpy(&cy, &data[offset + sizeof(i32)], sizeof(i32));
            std::memcpy(&chunk_id, &data[offset + sizeof(i32) * 2], sizeof(u32));
            std::memcpy(&flags, &data[offset + sizeof(i32) * 2 + sizeof(u32)], sizeof(u32));

            chunk = d_world_get_or_create_chunk(w, cx, cy);
            if (!chunk) {
                d_world_destroy(w);
                status = "Chunk alloc failed.";
                return false;
            }
            chunk->chunk_id = chunk_id;
            chunk->flags = (u16)flags;

            chunk_blob.ptr = const_cast<unsigned char *>(&data[offset + meta_size]);
            chunk_blob.len = len - (u32)meta_size;
            if (d_serialize_load_chunk_all(w, chunk, &chunk_blob) != 0) {
                d_world_destroy(w);
                status = "Chunk load failed.";
                return false;
            }
        }
        offset += len;
    }

    if (offset != data.size()) {
        d_world_destroy(w);
        status = "Trailing bytes in save blob.";
        return false;
    }

    if (m_world) {
        d_world_destroy(m_world);
    }
    m_world = w;
    m_hash = (unsigned long long)d_sim_hash_world(m_world);
    m_format = "GAME_SAVE_V1";
    status = "Loaded.";
    return true;
}

bool DomSaveInspectorController::load(const std::string &path, std::string &status) {
    std::vector<unsigned char> data;
    std::string err;

    if (!read_file(path, data, &err)) {
        status = err.empty() ? "Failed to read file." : err;
        return false;
    }

    if (has_dwrl_header(data)) {
        d_world *w = d_world_load_tlv(path.c_str());
        if (!w) {
            status = "Failed to load DWRL world.";
            return false;
        }
        if (m_world) {
            d_world_destroy(m_world);
        }
        m_world = w;
        m_hash = (unsigned long long)d_sim_hash_world(m_world);
        m_format = "DWRL_WORLD_V2";
        status = "Loaded.";
        return true;
    }

    return load_game_save_blob(data, status);
}

bool DomSaveInspectorController::validate(std::string &status) {
    if (!m_world) {
        status = "Nothing loaded.";
        return false;
    }
    m_hash = (unsigned long long)d_sim_hash_world(m_world);
    status = "Hash computed.";
    return true;
}

bool DomSaveInspectorController::save(const std::string &path, std::string &status) {
    (void)path;
    status = "Read-only tool (export TODO).";
    return false;
}

void DomSaveInspectorController::summary(std::string &out) const {
    char buf[256];
    if (!m_world) {
        out = "(none)";
        return;
    }
    std::sprintf(buf,
                 "%s chunks=%u hash=0x%016llx",
                 m_format.c_str(),
                 (unsigned)m_world->chunk_count,
                 (unsigned long long)m_hash);
    out = buf;
}

} // namespace tools
} // namespace dom

