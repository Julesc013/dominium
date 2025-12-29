/*
FILE: source/dominium/game/runtime/dom_game_save.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_save
RESPONSIBILITY: Implements DMSG save/load helpers for the runtime kernel; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (hash comparisons across save/load); see `docs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: DMSG v1 container; see `source/dominium/game/SPEC_SAVE.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_save.h"

#include <vector>
#include <string>
#include <cstdio>
#include <cstring>
#include <cstdlib>

#include "runtime/dom_game_runtime.h"
#include "dom_game_save.h"
#include "dom_session.h"

extern "C" {
#include "domino/sys.h"
#include "net/d_net_cmd.h"
}

namespace {

enum {
    DMSG_VERSION = 1u,
    DMSG_ENDIAN = 0x0000FFFEu,
    DMSG_CORE_VERSION = 1u,
    DMSG_RNG_VERSION = 1u
};

enum {
    CONTENT_TAG_PACKSET_ID = 0x0001u,
    CONTENT_TAG_PACK_HASH = 0x0002u,
    CONTENT_TAG_MOD_HASH = 0x0003u,
    CONTENT_TAG_INSTANCE_ID = 0x0004u
};

static const u64 FNV_OFFSET = 14695981039346656037ull;
static const u64 FNV_PRIME = 1099511628211ull;

static u32 read_u32_le(const unsigned char *p) {
    return (u32)p[0] |
           ((u32)p[1] << 8) |
           ((u32)p[2] << 16) |
           ((u32)p[3] << 24);
}

static u64 read_u64_le(const unsigned char *p) {
    return (u64)read_u32_le(p) | ((u64)read_u32_le(p + 4u) << 32u);
}

static void write_u32_le(unsigned char out[4], u32 v) {
    out[0] = (unsigned char)(v & 0xffu);
    out[1] = (unsigned char)((v >> 8u) & 0xffu);
    out[2] = (unsigned char)((v >> 16u) & 0xffu);
    out[3] = (unsigned char)((v >> 24u) & 0xffu);
}

static void write_u64_le(unsigned char out[8], u64 v) {
    write_u32_le(out, (u32)(v & 0xffffffffull));
    write_u32_le(out + 4u, (u32)((v >> 32u) & 0xffffffffull));
}

static void append_bytes(std::vector<unsigned char> &out, const void *data, size_t len) {
    const size_t base = out.size();
    out.resize(base + len);
    if (len > 0u && data) {
        std::memcpy(&out[base], data, len);
    }
}

static void append_u32_le(std::vector<unsigned char> &out, u32 v) {
    unsigned char buf[4];
    write_u32_le(buf, v);
    append_bytes(out, buf, 4u);
}

static void append_u64_le(std::vector<unsigned char> &out, u64 v) {
    unsigned char buf[8];
    write_u64_le(buf, v);
    append_bytes(out, buf, 8u);
}

static void append_tlv(std::vector<unsigned char> &out, u32 tag, const unsigned char *payload, u32 len) {
    append_u32_le(out, tag);
    append_u32_le(out, len);
    append_bytes(out, payload, (size_t)len);
}

static void append_tlv_u64(std::vector<unsigned char> &out, u32 tag, u64 value) {
    unsigned char buf[8];
    write_u64_le(buf, value);
    append_tlv(out, tag, buf, 8u);
}

static u64 fnv1a64_update(u64 h, const unsigned char *data, size_t len) {
    size_t i;
    if (!data || len == 0u) {
        return h;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= FNV_PRIME;
    }
    return h;
}

static u64 fnv1a64_bytes(const unsigned char *data, size_t len) {
    return fnv1a64_update(FNV_OFFSET, data, len);
}

static int str_ieq(const std::string &a, const char *b) {
    size_t i;
    if (!b) {
        return 0;
    }
    if (a.size() != std::strlen(b)) {
        return 0;
    }
    for (i = 0u; i < a.size(); ++i) {
        char ca = a[i];
        char cb = b[i];
        if (ca >= 'A' && ca <= 'Z') ca = static_cast<char>(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = static_cast<char>(cb - 'A' + 'a');
        if (ca != cb) {
            return 0;
        }
    }
    return 1;
}

static int is_base_id(const std::string &id) {
    return str_ieq(id, "base") != 0;
}

static u64 hash_pack_entry(u64 h, const char *prefix, const std::string &id, u32 version) {
    char ver_buf[32];
    int wrote;

    if (prefix && prefix[0]) {
        h = fnv1a64_update(h, (const unsigned char *)prefix, std::strlen(prefix));
    }
    h = fnv1a64_update(h, (const unsigned char *)id.c_str(), id.size());
    h = fnv1a64_update(h, (const unsigned char *)":", 1u);

    wrote = std::snprintf(ver_buf, sizeof(ver_buf), "%u", (unsigned)version);
    if (wrote > 0) {
        h = fnv1a64_update(h, (const unsigned char *)ver_buf, (size_t)wrote);
    }
    h = fnv1a64_update(h, (const unsigned char *)";", 1u);
    return h;
}

static u64 compute_packset_id(const dom::InstanceInfo &inst, const dom::PackSet *pset) {
    u64 h = FNV_OFFSET;
    bool base_added = false;
    size_t i;

    if (pset && pset->base_loaded) {
        h = hash_pack_entry(h, "pack:", std::string("base"), pset->base_version);
        base_added = true;
    }

    for (i = 0u; i < inst.packs.size(); ++i) {
        const dom::PackRef &pref = inst.packs[i];
        if (is_base_id(pref.id)) {
            if (!base_added) {
                h = hash_pack_entry(h, "pack:", pref.id, pref.version);
                base_added = true;
            }
            continue;
        }
        h = hash_pack_entry(h, "pack:", pref.id, pref.version);
    }

    for (i = 0u; i < inst.mods.size(); ++i) {
        const dom::ModRef &mref = inst.mods[i];
        h = hash_pack_entry(h, "mod:", mref.id, mref.version);
    }

    return h;
}

static void build_content_tlv(const dom::DomSession *session, std::vector<unsigned char> &out) {
    out.clear();
    if (!session) {
        return;
    }

    {
        const dom::InstanceInfo &inst = session->instance();
        const dom::PackSet &pset = session->packset();
        const u64 packset_id = compute_packset_id(inst, &pset);
        append_tlv_u64(out, CONTENT_TAG_PACKSET_ID, packset_id);

        if (!pset.pack_blobs.empty()) {
            size_t i;
            for (i = 0u; i < pset.pack_blobs.size(); ++i) {
                const d_tlv_blob &blob = pset.pack_blobs[i];
                const u64 h = fnv1a64_bytes(blob.ptr, blob.len);
                append_tlv_u64(out, CONTENT_TAG_PACK_HASH, h);
            }
        }
        if (!pset.mod_blobs.empty()) {
            size_t i;
            for (i = 0u; i < pset.mod_blobs.size(); ++i) {
                const d_tlv_blob &blob = pset.mod_blobs[i];
                const u64 h = fnv1a64_bytes(blob.ptr, blob.len);
                append_tlv_u64(out, CONTENT_TAG_MOD_HASH, h);
            }
        }

        if (!inst.id.empty()) {
            const u32 len = (u32)inst.id.size();
            append_tlv(out, CONTENT_TAG_INSTANCE_ID,
                       (const unsigned char *)inst.id.c_str(), len);
        }
    }
}

static bool write_file(const char *path, const unsigned char *data, size_t len) {
    void *fh;
    size_t wrote;
    if (!path || !path[0]) {
        return false;
    }
    fh = dsys_file_open(path, "wb");
    if (!fh) {
        return false;
    }
    wrote = dsys_file_write(fh, data, len);
    dsys_file_close(fh);
    return wrote == len;
}

static bool read_file_alloc(const char *path, unsigned char **out_data, size_t *out_len) {
    void *fh;
    long size;
    size_t read_len;
    unsigned char *buf;

    if (!path || !path[0] || !out_data || !out_len) {
        return false;
    }

    fh = dsys_file_open(path, "rb");
    if (!fh) {
        return false;
    }
    if (dsys_file_seek(fh, 0L, SEEK_END) != 0) {
        dsys_file_close(fh);
        return false;
    }
    size = dsys_file_tell(fh);
    if (size <= 0L) {
        dsys_file_close(fh);
        return false;
    }
    if (dsys_file_seek(fh, 0L, SEEK_SET) != 0) {
        dsys_file_close(fh);
        return false;
    }

    buf = (unsigned char *)std::malloc((size_t)size);
    if (!buf) {
        dsys_file_close(fh);
        return false;
    }
    read_len = dsys_file_read(fh, buf, (size_t)size);
    dsys_file_close(fh);
    if (read_len != (size_t)size) {
        std::free(buf);
        return false;
    }

    *out_data = buf;
    *out_len = (size_t)size;
    return true;
}

static int parse_dmsg(const unsigned char *data, size_t len, dom_game_save_desc *out_desc) {
    u32 version;
    u32 endian;
    u32 ups;
    u64 tick_index;
    u64 seed;
    u32 content_len;
    size_t offset;

    const unsigned char *core_ptr = (const unsigned char *)0;
    u32 core_len = 0u;
    u32 core_version = 0u;

    u32 rng_state = 0u;
    u32 rng_version = 0u;
    int has_rng = 0;

    if (!data || !out_desc) {
        return DOM_GAME_SAVE_ERR;
    }
    if (len < 36u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (std::memcmp(data, "DMSG", 4u) != 0) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    version = read_u32_le(data + 4u);
    if (version != DMSG_VERSION) {
        return (version > DMSG_VERSION) ? DOM_GAME_SAVE_ERR_MIGRATION : DOM_GAME_SAVE_ERR_FORMAT;
    }
    endian = read_u32_le(data + 8u);
    if (endian != DMSG_ENDIAN) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    ups = read_u32_le(data + 12u);
    tick_index = read_u64_le(data + 16u);
    seed = read_u64_le(data + 24u);
    content_len = read_u32_le(data + 32u);

    offset = 36u;
    if ((size_t)content_len > len - offset) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    offset += (size_t)content_len;

    while (offset < len) {
        const unsigned char *tag;
        u32 chunk_version;
        u32 chunk_size;
        if (offset + 12u > len) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        tag = data + offset;
        chunk_version = read_u32_le(data + offset + 4u);
        chunk_size = read_u32_le(data + offset + 8u);
        offset += 12u;
        if ((size_t)chunk_size > len - offset) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }

        if (std::memcmp(tag, "CORE", 4u) == 0) {
            if (chunk_version > DMSG_CORE_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_CORE_VERSION || chunk_size == 0u || core_ptr) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            core_ptr = data + offset;
            core_len = chunk_size;
            core_version = chunk_version;
        } else if (std::memcmp(tag, "RNG ", 4u) == 0) {
            if (chunk_version > DMSG_RNG_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_RNG_VERSION || has_rng || chunk_size != 4u) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            rng_state = read_u32_le(data + offset);
            rng_version = chunk_version;
            has_rng = 1;
        }

        offset += (size_t)chunk_size;
    }

    if (!core_ptr || !has_rng) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    std::memset(out_desc, 0, sizeof(*out_desc));
    out_desc->struct_size = (u32)sizeof(*out_desc);
    out_desc->struct_version = DOM_GAME_SAVE_DESC_VERSION;
    out_desc->container_version = version;
    out_desc->ups = ups;
    out_desc->tick_index = tick_index;
    out_desc->seed = seed;
    out_desc->content_tlv = (content_len > 0u) ? (data + 36u) : (const unsigned char *)0;
    out_desc->content_tlv_len = content_len;
    out_desc->core_blob = core_ptr;
    out_desc->core_blob_len = core_len;
    out_desc->core_version = core_version;
    out_desc->rng_state = rng_state;
    out_desc->rng_version = rng_version;
    out_desc->has_rng = (u32)has_rng;
    return DOM_GAME_SAVE_OK;
}

static bool build_save_bytes(const dom_game_runtime *rt, std::vector<unsigned char> &out) {
    d_world *world;
    const dom::DomSession *session;
    std::vector<unsigned char> core_blob;
    std::vector<unsigned char> content_tlv;
    u32 ups;
    u64 tick;
    u64 seed;

    if (!rt) {
        return false;
    }
    world = dom_game_runtime_world((dom_game_runtime *)rt);
    if (!world) {
        return false;
    }

    ups = dom_game_runtime_get_ups(rt);
    tick = dom_game_runtime_get_tick(rt);
    seed = dom_game_runtime_get_seed(rt);
    if (ups == 0u) {
        return false;
    }

    if (!dom::game_save_world_blob(world, core_blob) || core_blob.empty()) {
        return false;
    }

    session = (const dom::DomSession *)dom_game_runtime_session(rt);
    build_content_tlv(session, content_tlv);

    if (content_tlv.size() > 0xffffffffull || core_blob.size() > 0xffffffffull) {
        return false;
    }

    out.clear();
    append_bytes(out, "DMSG", 4u);
    append_u32_le(out, DMSG_VERSION);
    append_u32_le(out, DMSG_ENDIAN);
    append_u32_le(out, ups);
    append_u64_le(out, tick);
    append_u64_le(out, seed);
    append_u32_le(out, (u32)content_tlv.size());
    append_bytes(out, content_tlv.empty() ? (const unsigned char *)0 : &content_tlv[0], content_tlv.size());

    append_bytes(out, "CORE", 4u);
    append_u32_le(out, DMSG_CORE_VERSION);
    append_u32_le(out, (u32)core_blob.size());
    append_bytes(out, &core_blob[0], core_blob.size());

    append_bytes(out, "RNG ", 4u);
    append_u32_le(out, DMSG_RNG_VERSION);
    append_u32_le(out, 4u);
    append_u32_le(out, world->rng.state);
    return true;
}

} // namespace

extern "C" {

int dom_game_save_read(const char *path,
                       dom_game_save_desc *out_desc,
                       unsigned char **out_storage,
                       u32 *out_storage_len) {
    unsigned char *data = (unsigned char *)0;
    size_t data_len = 0u;
    int rc;

    if (!path || !out_desc || !out_storage || !out_storage_len) {
        return DOM_GAME_SAVE_ERR;
    }

    *out_storage = (unsigned char *)0;
    *out_storage_len = 0u;

    if (!read_file_alloc(path, &data, &data_len)) {
        return DOM_GAME_SAVE_ERR;
    }
    if (data_len > 0xffffffffull) {
        std::free(data);
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    rc = parse_dmsg(data, data_len, out_desc);
    if (rc != DOM_GAME_SAVE_OK) {
        std::free(data);
        return rc;
    }

    *out_storage = data;
    *out_storage_len = (u32)data_len;
    return DOM_GAME_SAVE_OK;
}

void dom_game_save_release(unsigned char *storage) {
    if (storage) {
        std::free(storage);
    }
}

int dom_game_save_write(const char *path,
                        const dom_game_runtime *rt,
                        u32 flags) {
    std::vector<unsigned char> bytes;
    (void)flags;

    if (!path || !path[0] || !rt) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!build_save_bytes(rt, bytes) || bytes.empty()) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!write_file(path, &bytes[0], bytes.size())) {
        return DOM_GAME_SAVE_ERR;
    }
    return DOM_GAME_SAVE_OK;
}

int dom_game_runtime_save(dom_game_runtime *rt, const char *path) {
    return dom_game_save_write(path, rt, 0u);
}

int dom_game_runtime_load_save(dom_game_runtime *rt, const char *path) {
    dom_game_save_desc desc;
    unsigned char *storage = (unsigned char *)0;
    u32 storage_len = 0u;
    d_world *world;
    d_sim_context *sim;
    int rc;

    if (!rt || !path || !path[0]) {
        return DOM_GAME_SAVE_ERR;
    }

    std::memset(&desc, 0, sizeof(desc));
    rc = dom_game_save_read(path, &desc, &storage, &storage_len);
    if (rc != DOM_GAME_SAVE_OK) {
        if (rc == DOM_GAME_SAVE_ERR_MIGRATION) {
            std::fprintf(stderr, "DMSG load: migration required (version unsupported)\n");
        }
        return rc;
    }

    world = dom_game_runtime_world(rt);
    sim = dom_game_runtime_sim(rt);
    if (!world || !sim) {
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR;
    }
    if (desc.ups == 0u || desc.ups != dom_game_runtime_get_ups(rt)) {
        std::fprintf(stderr, "DMSG load: UPS mismatch (save=%u runtime=%u)\n",
                     (unsigned)desc.ups,
                     (unsigned)dom_game_runtime_get_ups(rt));
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR;
    }
    if (desc.tick_index > 0xffffffffull) {
        std::fprintf(stderr, "DMSG load: tick index out of range (%llu)\n",
                     (unsigned long long)desc.tick_index);
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (!desc.core_blob || desc.core_blob_len == 0u || !desc.has_rng) {
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    if (!dom::game_load_world_blob(world,
                                   desc.core_blob,
                                   desc.core_blob_len)) {
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR;
    }

    {
        const u32 tick = (u32)desc.tick_index;
        world->tick_count = tick;
        world->meta.seed = desc.seed;
        world->worldgen_seed = desc.seed;
        world->rng.state = desc.rng_state;
        sim->tick_index = tick;
    }

    (void)d_net_cmd_queue_init();
    dom_game_save_release(storage);
    return DOM_GAME_SAVE_OK;
}

} /* extern "C" */
