/*
FILE: source/dominium/game/runtime/dom_game_content_id.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_content_id
RESPONSIBILITY: Implements helpers for building content identity TLVs; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (content identity hashing).
VERSIONING / ABI / DATA FORMAT NOTES: TLV tags defined in `source/dominium/game/SPEC_SAVE.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_content_id.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "dom_session.h"

namespace {

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

struct ContentSummary {
    bool has_packset_id;
    u64 packset_id;
    std::vector<u64> pack_hashes;
    std::vector<u64> mod_hashes;
    bool has_instance_id;
    std::string instance_id;
};

static void build_local_summary(const dom::DomSession *session, ContentSummary &out) {
    out.has_packset_id = false;
    out.packset_id = 0ull;
    out.pack_hashes.clear();
    out.mod_hashes.clear();
    out.has_instance_id = false;
    out.instance_id.clear();

    if (!session) {
        return;
    }

    const dom::InstanceInfo &inst = session->instance();
    const dom::PackSet &pset = session->packset();
    out.packset_id = compute_packset_id(inst, &pset);
    out.has_packset_id = true;

    if (!pset.pack_blobs.empty()) {
        size_t i;
        out.pack_hashes.reserve(pset.pack_blobs.size());
        for (i = 0u; i < pset.pack_blobs.size(); ++i) {
            const d_tlv_blob &blob = pset.pack_blobs[i];
            out.pack_hashes.push_back(fnv1a64_bytes(blob.ptr, blob.len));
        }
    }

    if (!pset.mod_blobs.empty()) {
        size_t i;
        out.mod_hashes.reserve(pset.mod_blobs.size());
        for (i = 0u; i < pset.mod_blobs.size(); ++i) {
            const d_tlv_blob &blob = pset.mod_blobs[i];
            out.mod_hashes.push_back(fnv1a64_bytes(blob.ptr, blob.len));
        }
    }

    if (!inst.id.empty()) {
        out.has_instance_id = true;
        out.instance_id = inst.id;
    }
}

static bool parse_tlv_summary(const unsigned char *tlv, u32 len, ContentSummary &out) {
    size_t offset = 0u;

    out.has_packset_id = false;
    out.packset_id = 0ull;
    out.pack_hashes.clear();
    out.mod_hashes.clear();
    out.has_instance_id = false;
    out.instance_id.clear();

    if (len == 0u) {
        return true;
    }
    if (!tlv) {
        return false;
    }

    while (offset < len) {
        const unsigned char *payload;
        u32 tag;
        u32 tlen;
        if (len - offset < 8u) {
            return false;
        }
        tag = read_u32_le(tlv + offset);
        tlen = read_u32_le(tlv + offset + 4u);
        offset += 8u;
        if ((size_t)tlen > len - offset) {
            return false;
        }
        payload = tlv + offset;

        if (tag == CONTENT_TAG_PACKSET_ID) {
            if (tlen != 8u || out.has_packset_id) {
                return false;
            }
            out.packset_id = read_u64_le(payload);
            out.has_packset_id = true;
        } else if (tag == CONTENT_TAG_PACK_HASH) {
            if (tlen != 8u) {
                return false;
            }
            out.pack_hashes.push_back(read_u64_le(payload));
        } else if (tag == CONTENT_TAG_MOD_HASH) {
            if (tlen != 8u) {
                return false;
            }
            out.mod_hashes.push_back(read_u64_le(payload));
        } else if (tag == CONTENT_TAG_INSTANCE_ID) {
            if (out.has_instance_id) {
                return false;
            }
            out.instance_id.assign(reinterpret_cast<const char *>(payload),
                                    reinterpret_cast<const char *>(payload + tlen));
            out.has_instance_id = true;
        }

        offset += (size_t)tlen;
    }

    return true;
}

} // namespace

namespace dom {

bool dom_game_content_build_tlv(const DomSession *session,
                                std::vector<unsigned char> &out) {
    ContentSummary summary;

    out.clear();
    if (!session) {
        return false;
    }

    build_local_summary(session, summary);

    if (summary.has_packset_id) {
        append_tlv_u64(out, CONTENT_TAG_PACKSET_ID, summary.packset_id);
    }

    if (!summary.pack_hashes.empty()) {
        size_t i;
        for (i = 0u; i < summary.pack_hashes.size(); ++i) {
            append_tlv_u64(out, CONTENT_TAG_PACK_HASH, summary.pack_hashes[i]);
        }
    }

    if (!summary.mod_hashes.empty()) {
        size_t i;
        for (i = 0u; i < summary.mod_hashes.size(); ++i) {
            append_tlv_u64(out, CONTENT_TAG_MOD_HASH, summary.mod_hashes[i]);
        }
    }

    if (summary.has_instance_id) {
        const u32 len = (u32)summary.instance_id.size();
        append_tlv(out, CONTENT_TAG_INSTANCE_ID,
                   (const unsigned char *)summary.instance_id.c_str(), len);
    }

    return true;
}

bool dom_game_content_match_tlv(const DomSession *session,
                                const unsigned char *tlv,
                                u32 len) {
    ContentSummary local;
    ContentSummary file;

    if (!session) {
        return false;
    }
    if (!parse_tlv_summary(tlv, len, file)) {
        return false;
    }

    build_local_summary(session, local);

    if (file.has_packset_id) {
        if (!local.has_packset_id || local.packset_id != file.packset_id) {
            return false;
        }
    }
    if (!file.pack_hashes.empty()) {
        size_t i;
        if (local.pack_hashes.size() != file.pack_hashes.size()) {
            return false;
        }
        for (i = 0u; i < file.pack_hashes.size(); ++i) {
            if (local.pack_hashes[i] != file.pack_hashes[i]) {
                return false;
            }
        }
    }
    if (!file.mod_hashes.empty()) {
        size_t i;
        if (local.mod_hashes.size() != file.mod_hashes.size()) {
            return false;
        }
        for (i = 0u; i < file.mod_hashes.size(); ++i) {
            if (local.mod_hashes[i] != file.mod_hashes[i]) {
                return false;
            }
        }
    }
    if (file.has_instance_id) {
        if (!local.has_instance_id || local.instance_id != file.instance_id) {
            return false;
        }
    }

    return true;
}

} // namespace dom
