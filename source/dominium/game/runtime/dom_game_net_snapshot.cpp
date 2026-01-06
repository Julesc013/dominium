/*
FILE: source/dominium/game/runtime/dom_game_net_snapshot.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_net_snapshot
RESPONSIBILITY: Implements minimal server-auth snapshot container (v0).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Serialization is deterministic and uses explicit little-endian encodings.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_net_snapshot.h"

#include <cstring>

#include "dominium/core_tlv.h"
#include "domino/io/container.h"
#include "dom_session.h"
#include "runtime/dom_game_content_id.h"
#include "runtime/dom_game_runtime.h"

namespace {

static u64 compute_content_hash(const dom::DomSession *session) {
    std::vector<unsigned char> tlv;
    if (!session) {
        return 0ull;
    }
    if (!dom::dom_game_content_build_tlv(session, tlv)) {
        return 0ull;
    }
    if (tlv.empty()) {
        return 0ull;
    }
    return dom::core_tlv::tlv_fnv1a64(&tlv[0], tlv.size());
}

static int read_u32_from_tlv(const unsigned char *payload, u32 len, u32 *out) {
    if (!payload || len != 4u || !out) {
        return 0;
    }
    *out = dtlv_le_read_u32(payload);
    return 1;
}

static int read_u64_from_tlv(const unsigned char *payload, u32 len, u64 *out) {
    if (!payload || len != 8u || !out) {
        return 0;
    }
    *out = dtlv_le_read_u64(payload);
    return 1;
}

static int parse_tlv_block(const unsigned char *data,
                           u32 len,
                           u32 tag_a,
                           u32 tag_b,
                           u64 *out_b,
                           u32 *out_a) {
    u32 offset = 0u;
    u32 tag = 0u;
    const unsigned char *payload = 0;
    u32 payload_len = 0u;
    int seen_a = 0;
    int seen_b = 0;

    while (dtlv_tlv_next(data, len, &offset, &tag, &payload, &payload_len) == 0) {
        if (tag == tag_a && out_a && read_u32_from_tlv(payload, payload_len, out_a)) {
            seen_a = 1;
        } else if (tag == tag_b && out_b && read_u64_from_tlv(payload, payload_len, out_b)) {
            seen_b = 1;
        }
    }
    return (seen_a || !out_a) && (seen_b || !out_b);
}

static int parse_count_block(const unsigned char *data, u32 len, u32 tag, u32 *out_count) {
    u32 offset = 0u;
    u32 t = 0u;
    const unsigned char *payload = 0;
    u32 payload_len = 0u;
    while (dtlv_tlv_next(data, len, &offset, &t, &payload, &payload_len) == 0) {
        if (t == tag) {
            return read_u32_from_tlv(payload, payload_len, out_count);
        }
    }
    return 0;
}

} // namespace

int dom_game_net_snapshot_build(const dom_game_runtime *rt,
                                const dom_game_net_snapshot_opts *opts,
                                std::vector<unsigned char> &out_bytes) {
    dtlv_writer writer;
    unsigned char buf[8];
    const u32 ups = dom_game_runtime_get_ups(rt);
    const u64 tick = dom_game_runtime_get_tick(rt);
    const u64 content_hash = compute_content_hash(
        static_cast<const dom::DomSession *>(dom_game_runtime_session(rt)));
    const u32 vessel_count = 0u;
    const u32 surface_count = 0u;
    const u32 cap = 4096u;
    u32 detail_level = 100u;
    u32 interest_radius_m = 1024u;
    u32 assist_flags = 0u;
    int include_vesl = 1;
    int include_surf = 1;

    if (!rt || ups == 0u) {
        return DOM_NET_SNAPSHOT_ERR;
    }
    if (opts &&
        opts->struct_size >= sizeof(*opts) &&
        opts->struct_version == DOM_GAME_NET_SNAPSHOT_OPTS_VERSION) {
        detail_level = opts->detail_level;
        interest_radius_m = opts->interest_radius_m;
        assist_flags = opts->assist_flags;
    }
    if (detail_level < 25u) {
        include_vesl = 0;
    }
    if (detail_level < 50u || interest_radius_m == 0u) {
        include_surf = 0;
    }
    if ((assist_flags & DOM_NET_SNAPSHOT_ASSIST_LOCAL_CACHE) != 0u) {
        include_surf = 0;
    }

    out_bytes.assign(cap, 0u);
    dtlv_writer_init(&writer);
    if (dtlv_writer_init_mem(&writer, &out_bytes[0], cap) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }

    if (dtlv_writer_begin_chunk(&writer, DOM_NET_SNAPSHOT_CHUNK_TIME,
                                DOM_NET_SNAPSHOT_TIME_VERSION, 0u) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }
    dtlv_le_write_u32(buf, ups);
    if (dtlv_writer_write_tlv(&writer, DOM_NET_SNAPSHOT_TLV_UPS, buf, 4u) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }
    dtlv_le_write_u64(buf, tick);
    if (dtlv_writer_write_tlv(&writer, DOM_NET_SNAPSHOT_TLV_TICK, buf, 8u) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }
    if (dtlv_writer_end_chunk(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }

    if (dtlv_writer_begin_chunk(&writer, DOM_NET_SNAPSHOT_CHUNK_IDEN,
                                DOM_NET_SNAPSHOT_IDEN_VERSION, 0u) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }
    dtlv_le_write_u64(buf, content_hash);
    if (dtlv_writer_write_tlv(&writer, DOM_NET_SNAPSHOT_TLV_CONTENT_HASH64, buf, 8u) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }
    if (dtlv_writer_end_chunk(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }

    if (include_vesl) {
        if (dtlv_writer_begin_chunk(&writer, DOM_NET_SNAPSHOT_CHUNK_VESL,
                                    DOM_NET_SNAPSHOT_VESL_VERSION, 0u) != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_NET_SNAPSHOT_ERR;
        }
        dtlv_le_write_u32(buf, vessel_count);
        if (dtlv_writer_write_tlv(&writer, DOM_NET_SNAPSHOT_TLV_VESSEL_COUNT, buf, 4u) != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_NET_SNAPSHOT_ERR;
        }
        if (dtlv_writer_end_chunk(&writer) != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_NET_SNAPSHOT_ERR;
        }
    }

    if (include_surf) {
        if (dtlv_writer_begin_chunk(&writer, DOM_NET_SNAPSHOT_CHUNK_SURF,
                                    DOM_NET_SNAPSHOT_SURF_VERSION, 0u) != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_NET_SNAPSHOT_ERR;
        }
        dtlv_le_write_u32(buf, surface_count);
        if (dtlv_writer_write_tlv(&writer, DOM_NET_SNAPSHOT_TLV_SURFACE_COUNT, buf, 4u) != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_NET_SNAPSHOT_ERR;
        }
        if (dtlv_writer_end_chunk(&writer) != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_NET_SNAPSHOT_ERR;
        }
    }

    if (dtlv_writer_finalize(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_NET_SNAPSHOT_ERR;
    }

    out_bytes.resize(dtlv_writer_mem_size(&writer));
    dtlv_writer_dispose(&writer);
    return DOM_NET_SNAPSHOT_OK;
}

int dom_game_net_snapshot_parse(const unsigned char *data,
                                size_t len,
                                dom_game_net_snapshot_desc *out_desc) {
    dtlv_reader reader;
    const dtlv_dir_entry *time_entry;
    const dtlv_dir_entry *iden_entry;
    const dtlv_dir_entry *vesl_entry;
    const dtlv_dir_entry *surf_entry;
    const unsigned char *payload = 0;
    u32 payload_len = 0u;
    u32 ups = 0u;
    u64 tick = 0ull;
    u64 content_hash = 0ull;
    u32 vessel_count = 0u;
    u32 surface_count = 0u;

    if (!out_desc) {
        return DOM_NET_SNAPSHOT_ERR;
    }
    std::memset(out_desc, 0, sizeof(*out_desc));

    dtlv_reader_init(&reader);
    if (dtlv_reader_init_mem(&reader, data, (u64)len) != 0) {
        dtlv_reader_dispose(&reader);
        return DOM_NET_SNAPSHOT_FORMAT;
    }

    time_entry = dtlv_reader_find_first(&reader, DOM_NET_SNAPSHOT_CHUNK_TIME,
                                        DOM_NET_SNAPSHOT_TIME_VERSION);
    iden_entry = dtlv_reader_find_first(&reader, DOM_NET_SNAPSHOT_CHUNK_IDEN,
                                        DOM_NET_SNAPSHOT_IDEN_VERSION);
    vesl_entry = dtlv_reader_find_first(&reader, DOM_NET_SNAPSHOT_CHUNK_VESL,
                                        DOM_NET_SNAPSHOT_VESL_VERSION);
    surf_entry = dtlv_reader_find_first(&reader, DOM_NET_SNAPSHOT_CHUNK_SURF,
                                        DOM_NET_SNAPSHOT_SURF_VERSION);

    if (!time_entry || !iden_entry) {
        dtlv_reader_dispose(&reader);
        return DOM_NET_SNAPSHOT_FORMAT;
    }

    if (dtlv_reader_chunk_memview(&reader, time_entry, &payload, &payload_len) != 0 ||
        !parse_tlv_block(payload, payload_len,
                         DOM_NET_SNAPSHOT_TLV_UPS,
                         DOM_NET_SNAPSHOT_TLV_TICK,
                         &tick, &ups)) {
        dtlv_reader_dispose(&reader);
        return DOM_NET_SNAPSHOT_FORMAT;
    }

    if (dtlv_reader_chunk_memview(&reader, iden_entry, &payload, &payload_len) != 0 ||
        !parse_tlv_block(payload, payload_len,
                         0u,
                         DOM_NET_SNAPSHOT_TLV_CONTENT_HASH64,
                         &content_hash, 0)) {
        dtlv_reader_dispose(&reader);
        return DOM_NET_SNAPSHOT_FORMAT;
    }

    if (vesl_entry) {
        if (dtlv_reader_chunk_memview(&reader, vesl_entry, &payload, &payload_len) != 0 ||
            !parse_count_block(payload, payload_len, DOM_NET_SNAPSHOT_TLV_VESSEL_COUNT,
                               &vessel_count)) {
            dtlv_reader_dispose(&reader);
            return DOM_NET_SNAPSHOT_FORMAT;
        }
    }

    if (surf_entry) {
        if (dtlv_reader_chunk_memview(&reader, surf_entry, &payload, &payload_len) != 0 ||
            !parse_count_block(payload, payload_len, DOM_NET_SNAPSHOT_TLV_SURFACE_COUNT,
                               &surface_count)) {
            dtlv_reader_dispose(&reader);
            return DOM_NET_SNAPSHOT_FORMAT;
        }
    }

    dtlv_reader_dispose(&reader);

    out_desc->ups = ups;
    out_desc->tick_index = tick;
    out_desc->content_hash64 = content_hash;
    out_desc->vessel_count = vessel_count;
    out_desc->surface_chunk_count = surface_count;
    return DOM_NET_SNAPSHOT_OK;
}
