/*
FILE: source/dominium/game/runtime/dom_game_replay.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_replay
RESPONSIBILITY: Implements DMRP replay record/playback helpers; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (recorded command payloads must be stable).
VERSIONING / ABI / DATA FORMAT NOTES: DMRP v4 container; see `source/dominium/game/SPEC_REPLAY.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_replay.h"

#include <vector>
#include <cstring>

#include "dominium/core_tlv.h"
#include "dom_feature_epoch.h"
#include "runtime/dom_io_guard.h"

extern "C" {
#include "domino/sys.h"
#include "net/d_net_proto.h"
}

namespace {

enum {
    DMRP_VERSION = 6u,
    DMRP_ENDIAN = 0x0000FFFEu,
    DMRP_IDENTITY_VERSION = 1u,
    DMRP_MEDIA_BINDINGS_VERSION = 1u,
    DMRP_WEATHER_BINDINGS_VERSION = 1u,
    DMRP_AERO_PROPS_VERSION = 1u,
    DMRP_AERO_STATE_VERSION = 1u,
    DMRP_MACRO_ECONOMY_VERSION = 1u,
    DMRP_MACRO_EVENTS_VERSION = 1u,
    DMRP_FACTIONS_VERSION = 1u,
    DMRP_AI_SCHED_VERSION = 1u
};

enum {
    DMRP_IDENTITY_TAG_INSTANCE_ID = 2u,
    DMRP_IDENTITY_TAG_RUN_ID = 3u,
    DMRP_IDENTITY_TAG_MANIFEST_HASH = 4u,
    DMRP_IDENTITY_TAG_CONTENT_HASH = 5u
};

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

static bool write_all(void *fh, const void *data, size_t len) {
    size_t wrote;
    if (!fh || (!data && len > 0u)) {
        return false;
    }
    wrote = dsys_file_write(fh, data, len);
    return wrote == len;
}

static bool read_file(const char *path, std::vector<unsigned char> &out) {
    void *fh;
    long size;
    size_t read_len;

    out.clear();
    if (!path || !path[0]) {
        return false;
    }
    if (!dom_io_guard_io_allowed()) {
        dom_io_guard_note_violation("replay_read", path);
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

    out.resize((size_t)size);
    read_len = dsys_file_read(fh, &out[0], (size_t)size);
    dsys_file_close(fh);
    if (read_len != (size_t)size) {
        out.clear();
        return false;
    }
    return true;
}

static bool build_identity_tlv(const char *instance_id,
                               u64 run_id,
                               const unsigned char *manifest_hash_bytes,
                               u32 manifest_hash_len,
                               const unsigned char *content_tlv,
                               u32 content_tlv_len,
                               std::vector<unsigned char> &out) {
    dom::core_tlv::TlvWriter w;
    const u64 content_hash = dom::core_tlv::tlv_fnv1a64(content_tlv, (size_t)content_tlv_len);
    const std::string inst_id = instance_id ? instance_id : "";
    const unsigned char *manifest_ptr = manifest_hash_bytes;
    u32 manifest_size = manifest_hash_len;

    if (!manifest_ptr) {
        manifest_size = 0u;
    }

    w.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DMRP_IDENTITY_VERSION);
    w.add_string(DMRP_IDENTITY_TAG_INSTANCE_ID, inst_id);
    w.add_u64(DMRP_IDENTITY_TAG_RUN_ID, run_id);
    w.add_bytes(DMRP_IDENTITY_TAG_MANIFEST_HASH, manifest_ptr, manifest_size);
    w.add_u64(DMRP_IDENTITY_TAG_CONTENT_HASH, content_hash);

    out = w.bytes();
    return true;
}

struct dom_game_replay_record_view {
    u64 tick;
    const unsigned char *payload;
    u32 size;
};

} // namespace

struct dom_game_replay_record {
    void *fh;
};

struct dom_game_replay_play {
    std::vector<unsigned char> data;
    std::vector<dom_game_replay_record_view> records;
    std::vector<dom_game_replay_packet> scratch;
    size_t cursor;
    u64 last_tick;
    int has_last_tick;
    u32 ups;
    u64 seed;
    u32 feature_epoch;
    const unsigned char *content_tlv;
    u32 content_tlv_len;
    const unsigned char *media_bindings_blob;
    u32 media_bindings_len;
    u32 media_bindings_version;
    const unsigned char *weather_bindings_blob;
    u32 weather_bindings_len;
    u32 weather_bindings_version;
    const unsigned char *aero_props_blob;
    u32 aero_props_len;
    u32 aero_props_version;
    const unsigned char *aero_state_blob;
    u32 aero_state_len;
    u32 aero_state_version;
    const unsigned char *macro_economy_blob;
    u32 macro_economy_len;
    u32 macro_economy_version;
    const unsigned char *macro_events_blob;
    u32 macro_events_len;
    u32 macro_events_version;
    const unsigned char *factions_blob;
    u32 factions_len;
    u32 factions_version;
    const unsigned char *ai_sched_blob;
    u32 ai_sched_len;
    u32 ai_sched_version;
};

extern "C" {

dom_game_replay_record *dom_game_replay_record_open(const char *path,
                                                    u32 ups,
                                                    u64 seed,
                                                    const char *instance_id,
                                                    u64 run_id,
                                                    const unsigned char *manifest_hash_bytes,
                                                    u32 manifest_hash_len,
                                                    const unsigned char *content_tlv,
                                                    u32 content_tlv_len,
                                                    const unsigned char *media_bindings_blob,
                                                    u32 media_bindings_len,
                                                    const unsigned char *weather_bindings_blob,
                                                    u32 weather_bindings_len,
                                                    const unsigned char *aero_props_blob,
                                                    u32 aero_props_len,
                                                    const unsigned char *aero_state_blob,
                                                    u32 aero_state_len,
                                                    const unsigned char *macro_economy_blob,
                                                    u32 macro_economy_len,
                                                    const unsigned char *macro_events_blob,
                                                    u32 macro_events_len,
                                                    const unsigned char *factions_blob,
                                                    u32 factions_len,
                                                    const unsigned char *ai_sched_blob,
                                                    u32 ai_sched_len) {
    dom_game_replay_record *rec;
    unsigned char buf32[4];
    unsigned char buf64[8];
    void *fh;
    std::vector<unsigned char> identity_tlv;

    if (!path || !path[0] || ups == 0u) {
        return (dom_game_replay_record *)0;
    }
    if (content_tlv_len > 0u && !content_tlv) {
        return (dom_game_replay_record *)0;
    }
    if (media_bindings_len > 0u && !media_bindings_blob) {
        return (dom_game_replay_record *)0;
    }
    if (weather_bindings_len > 0u && !weather_bindings_blob) {
        return (dom_game_replay_record *)0;
    }
    if (aero_props_len > 0u && !aero_props_blob) {
        return (dom_game_replay_record *)0;
    }
    if (aero_state_len > 0u && !aero_state_blob) {
        return (dom_game_replay_record *)0;
    }
    if (macro_economy_len > 0u && !macro_economy_blob) {
        return (dom_game_replay_record *)0;
    }
    if (macro_events_len > 0u && !macro_events_blob) {
        return (dom_game_replay_record *)0;
    }
    if (factions_len > 0u && !factions_blob) {
        return (dom_game_replay_record *)0;
    }
    if (ai_sched_len > 0u && !ai_sched_blob) {
        return (dom_game_replay_record *)0;
    }
    if (!dom_io_guard_io_allowed()) {
        dom_io_guard_note_violation("replay_record_open", path);
        return (dom_game_replay_record *)0;
    }
    if (!build_identity_tlv(instance_id,
                            run_id,
                            manifest_hash_bytes,
                            manifest_hash_len,
                            content_tlv,
                            content_tlv_len,
                            identity_tlv)) {
        return (dom_game_replay_record *)0;
    }
    if (identity_tlv.size() > 0xffffffffull) {
        return (dom_game_replay_record *)0;
    }
    if (media_bindings_len > 0xffffffffu || weather_bindings_len > 0xffffffffu ||
        aero_props_len > 0xffffffffu || aero_state_len > 0xffffffffu ||
        macro_economy_len > 0xffffffffu || macro_events_len > 0xffffffffu ||
        factions_len > 0xffffffffu || ai_sched_len > 0xffffffffu) {
        return (dom_game_replay_record *)0;
    }

    fh = dsys_file_open(path, "wb");
    if (!fh) {
        return (dom_game_replay_record *)0;
    }

    if (!write_all(fh, "DMRP", 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, DMRP_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, DMRP_ENDIAN);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, ups);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u64_le(buf64, seed);
    if (!write_all(fh, buf64, 8u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, dom::dom_feature_epoch_current());
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, content_tlv_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (content_tlv_len > 0u) {
        if (!write_all(fh, content_tlv, content_tlv_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }
    write_u32_le(buf32, (u32)identity_tlv.size());
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (!identity_tlv.empty()) {
        if (!write_all(fh, &identity_tlv[0], identity_tlv.size())) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    write_u32_le(buf32, DMRP_MEDIA_BINDINGS_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, media_bindings_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (media_bindings_len > 0u) {
        if (!write_all(fh, media_bindings_blob, media_bindings_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    write_u32_le(buf32, DMRP_WEATHER_BINDINGS_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, weather_bindings_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (weather_bindings_len > 0u) {
        if (!write_all(fh, weather_bindings_blob, weather_bindings_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    write_u32_le(buf32, DMRP_AERO_PROPS_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, aero_props_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (aero_props_len > 0u) {
        if (!write_all(fh, aero_props_blob, aero_props_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    write_u32_le(buf32, DMRP_AERO_STATE_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, aero_state_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (aero_state_len > 0u) {
        if (!write_all(fh, aero_state_blob, aero_state_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    write_u32_le(buf32, DMRP_MACRO_ECONOMY_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, macro_economy_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (macro_economy_len > 0u) {
        if (!write_all(fh, macro_economy_blob, macro_economy_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    write_u32_le(buf32, DMRP_MACRO_EVENTS_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, macro_events_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (macro_events_len > 0u) {
        if (!write_all(fh, macro_events_blob, macro_events_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    write_u32_le(buf32, DMRP_FACTIONS_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, factions_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (factions_len > 0u) {
        if (!write_all(fh, factions_blob, factions_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    write_u32_le(buf32, DMRP_AI_SCHED_VERSION);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    write_u32_le(buf32, ai_sched_len);
    if (!write_all(fh, buf32, 4u)) {
        dsys_file_close(fh);
        return (dom_game_replay_record *)0;
    }
    if (ai_sched_len > 0u) {
        if (!write_all(fh, ai_sched_blob, ai_sched_len)) {
            dsys_file_close(fh);
            return (dom_game_replay_record *)0;
        }
    }

    rec = new dom_game_replay_record();
    rec->fh = fh;
    return rec;
}

void dom_game_replay_record_close(dom_game_replay_record *rec) {
    if (!rec) {
        return;
    }
    if (rec->fh) {
        dsys_file_close(rec->fh);
        rec->fh = (void *)0;
    }
    delete rec;
}

int dom_game_replay_record_write_cmd(dom_game_replay_record *rec,
                                     u64 tick,
                                     const unsigned char *payload,
                                     u32 size) {
    unsigned char buf64[8];
    unsigned char buf32[4];

    if (!rec || !rec->fh || !payload || size == 0u) {
        return DOM_GAME_REPLAY_ERR;
    }
    if (!dom_io_guard_io_allowed()) {
        dom_io_guard_note_violation("replay_record_write", "(stream)");
        return DOM_GAME_REPLAY_ERR;
    }

    write_u64_le(buf64, tick);
    if (!write_all(rec->fh, buf64, 8u)) {
        return DOM_GAME_REPLAY_ERR;
    }
    write_u32_le(buf32, (u32)D_NET_MSG_CMD);
    if (!write_all(rec->fh, buf32, 4u)) {
        return DOM_GAME_REPLAY_ERR;
    }
    write_u32_le(buf32, size);
    if (!write_all(rec->fh, buf32, 4u)) {
        return DOM_GAME_REPLAY_ERR;
    }
    if (!write_all(rec->fh, payload, size)) {
        return DOM_GAME_REPLAY_ERR;
    }

    return DOM_GAME_REPLAY_OK;
}

dom_game_replay_play *dom_game_replay_play_open(const char *path,
                                                dom_game_replay_desc *out_desc) {
    std::vector<unsigned char> data;
    dom_game_replay_play *play;
    size_t offset;
    size_t data_len;
    u32 version;
    u32 endian;
    u32 ups;
    u64 seed;
    u32 feature_epoch;
    u32 content_len;
    const unsigned char *content_ptr;
    const unsigned char *media_bindings_ptr = (const unsigned char *)0;
    u32 media_bindings_len = 0u;
    u32 media_bindings_version = 0u;
    int has_media_bindings = 0;
    const unsigned char *weather_bindings_ptr = (const unsigned char *)0;
    u32 weather_bindings_len = 0u;
    u32 weather_bindings_version = 0u;
    int has_weather_bindings = 0;
    const unsigned char *aero_props_ptr = (const unsigned char *)0;
    u32 aero_props_len = 0u;
    u32 aero_props_version = 0u;
    int has_aero_props = 0;
    const unsigned char *aero_state_ptr = (const unsigned char *)0;
    u32 aero_state_len = 0u;
    u32 aero_state_version = 0u;
    int has_aero_state = 0;
    const unsigned char *macro_economy_ptr = (const unsigned char *)0;
    u32 macro_economy_len = 0u;
    u32 macro_economy_version = 0u;
    int has_macro_economy = 0;
    const unsigned char *macro_events_ptr = (const unsigned char *)0;
    u32 macro_events_len = 0u;
    u32 macro_events_version = 0u;
    int has_macro_events = 0;
    const unsigned char *factions_ptr = (const unsigned char *)0;
    u32 factions_len = 0u;
    u32 factions_version = 0u;
    int has_factions = 0;
    const unsigned char *ai_sched_ptr = (const unsigned char *)0;
    u32 ai_sched_len = 0u;
    u32 ai_sched_version = 0u;
    int has_ai_sched = 0;
    const char *instance_id = (const char *)0;
    u32 instance_id_len = 0u;
    u64 run_id_val = 0ull;
    const unsigned char *manifest_hash = (const unsigned char *)0;
    u32 manifest_hash_len = 0u;
    u64 content_hash = 0ull;
    int has_content_hash = 0;
    int has_identity = 0;
    u64 last_tick = 0u;
    int has_last_tick = 0;
    u64 prev_tick = 0u;
    int has_prev_tick = 0;

    if (out_desc) {
        std::memset(out_desc, 0, sizeof(*out_desc));
        out_desc->struct_size = (u32)sizeof(*out_desc);
        out_desc->struct_version = DOM_GAME_REPLAY_DESC_VERSION;
        out_desc->error_code = DOM_GAME_REPLAY_OK;
    }

    if (!read_file(path, data)) {
        if (out_desc) {
            out_desc->error_code = DOM_GAME_REPLAY_ERR;
        }
        return (dom_game_replay_play *)0;
    }

    data_len = data.size();
    if (data_len < 28u) {
        if (out_desc) {
            out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
        }
        return (dom_game_replay_play *)0;
    }
    if (std::memcmp(&data[0], "DMRP", 4u) != 0) {
        if (out_desc) {
            out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
        }
        return (dom_game_replay_play *)0;
    }

    version = read_u32_le(&data[4]);
    if (out_desc) {
        out_desc->container_version = version;
    }
    if (version != DMRP_VERSION) {
        if (out_desc) {
            out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
        }
        return (dom_game_replay_play *)0;
    }
    endian = read_u32_le(&data[8]);
    if (endian != DMRP_ENDIAN) {
        if (out_desc) {
            out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
        }
        return (dom_game_replay_play *)0;
    }
    ups = read_u32_le(&data[12]);
    seed = read_u64_le(&data[16]);
    feature_epoch = dom::dom_feature_epoch_current();
    if (version >= 3u) {
        if (data_len < 32u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        feature_epoch = read_u32_le(&data[24]);
        if (feature_epoch == 0u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        if (!dom::dom_feature_epoch_supported(feature_epoch)) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        content_len = read_u32_le(&data[28]);
        offset = 32u;
    } else {
        content_len = read_u32_le(&data[24]);
        offset = 28u;
    }
    if ((size_t)content_len > data_len - offset) {
        if (out_desc) {
            out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
        }
        return (dom_game_replay_play *)0;
    }
    content_ptr = (content_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
    offset += (size_t)content_len;

    if (version >= 2u) {
        u32 identity_len = 0u;
        const unsigned char *identity_ptr = (const unsigned char *)0;
        if (data_len - offset < 4u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        identity_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)identity_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        if (identity_len == 0u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        identity_ptr = &data[offset];
        offset += (size_t)identity_len;

        {
            dom::core_tlv::TlvReader ir(identity_ptr, (size_t)identity_len);
            dom::core_tlv::TlvRecord irec;
            u32 schema_version = 0u;
            while (ir.next(irec)) {
                switch (irec.tag) {
                case dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION:
                    (void)dom::core_tlv::tlv_read_u32_le(irec.payload, irec.len, schema_version);
                    break;
                case DMRP_IDENTITY_TAG_INSTANCE_ID:
                    instance_id = (const char *)irec.payload;
                    instance_id_len = irec.len;
                    break;
                case DMRP_IDENTITY_TAG_RUN_ID:
                    (void)dom::core_tlv::tlv_read_u64_le(irec.payload, irec.len, run_id_val);
                    break;
                case DMRP_IDENTITY_TAG_MANIFEST_HASH:
                    manifest_hash = irec.payload;
                    manifest_hash_len = irec.len;
                    break;
                case DMRP_IDENTITY_TAG_CONTENT_HASH:
                    if (dom::core_tlv::tlv_read_u64_le(irec.payload, irec.len, content_hash)) {
                        has_content_hash = 1;
                    }
                    break;
                default:
                    break;
                }
            }
            if (schema_version != DMRP_IDENTITY_VERSION || !has_content_hash) {
                if (out_desc) {
                    out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
                }
                return (dom_game_replay_play *)0;
            }
            has_identity = 1;
        }
    }

    if (version >= 5u) {
        if (data_len - offset < 8u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        media_bindings_version = read_u32_le(&data[offset]);
        offset += 4u;
        if (media_bindings_version > DMRP_MEDIA_BINDINGS_VERSION) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        media_bindings_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)media_bindings_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        media_bindings_ptr = (media_bindings_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
        offset += (size_t)media_bindings_len;
        has_media_bindings = 1;

        if (data_len - offset < 8u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        weather_bindings_version = read_u32_le(&data[offset]);
        offset += 4u;
        if (weather_bindings_version > DMRP_WEATHER_BINDINGS_VERSION) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        weather_bindings_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)weather_bindings_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        weather_bindings_ptr = (weather_bindings_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
        offset += (size_t)weather_bindings_len;
        has_weather_bindings = 1;

        if (data_len - offset < 8u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        aero_props_version = read_u32_le(&data[offset]);
        offset += 4u;
        if (aero_props_version > DMRP_AERO_PROPS_VERSION) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        aero_props_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)aero_props_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        aero_props_ptr = (aero_props_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
        offset += (size_t)aero_props_len;
        has_aero_props = 1;

        if (data_len - offset < 8u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        aero_state_version = read_u32_le(&data[offset]);
        offset += 4u;
        if (aero_state_version > DMRP_AERO_STATE_VERSION) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        aero_state_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)aero_state_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        aero_state_ptr = (aero_state_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
        offset += (size_t)aero_state_len;
        has_aero_state = 1;
    }

    if (version >= 4u) {
        if (data_len - offset < 8u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        macro_economy_version = read_u32_le(&data[offset]);
        offset += 4u;
        if (macro_economy_version > DMRP_MACRO_ECONOMY_VERSION) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        macro_economy_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)macro_economy_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        macro_economy_ptr = (macro_economy_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
        offset += (size_t)macro_economy_len;
        has_macro_economy = 1;

        if (data_len - offset < 8u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        macro_events_version = read_u32_le(&data[offset]);
        offset += 4u;
        if (macro_events_version > DMRP_MACRO_EVENTS_VERSION) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        macro_events_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)macro_events_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        macro_events_ptr = (macro_events_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
        offset += (size_t)macro_events_len;
        has_macro_events = 1;
    }

    if (version >= 6u) {
        if (data_len - offset < 8u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        factions_version = read_u32_le(&data[offset]);
        offset += 4u;
        if (factions_version > DMRP_FACTIONS_VERSION) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        factions_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)factions_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        factions_ptr = (factions_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
        offset += (size_t)factions_len;
        has_factions = 1;

        if (data_len - offset < 8u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        ai_sched_version = read_u32_le(&data[offset]);
        offset += 4u;
        if (ai_sched_version > DMRP_AI_SCHED_VERSION) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_MIGRATION;
            }
            return (dom_game_replay_play *)0;
        }
        ai_sched_len = read_u32_le(&data[offset]);
        offset += 4u;
        if ((size_t)ai_sched_len > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        ai_sched_ptr = (ai_sched_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
        offset += (size_t)ai_sched_len;
        has_ai_sched = 1;
    }

    std::vector<dom_game_replay_record_view> records;
    while (offset < data_len) {
        u64 tick;
        u32 msg_kind;
        u32 size;
        const unsigned char *payload;

        if (data_len - offset < 16u) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        tick = read_u64_le(&data[offset]);
        msg_kind = read_u32_le(&data[offset + 8u]);
        size = read_u32_le(&data[offset + 12u]);
        offset += 16u;
        if ((size_t)size > data_len - offset) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        if (tick > 0xffffffffull) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }
        if (has_prev_tick && tick < prev_tick) {
            if (out_desc) {
                out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
            }
            return (dom_game_replay_play *)0;
        }

        payload = &data[offset];
        if (msg_kind == (u32)D_NET_MSG_CMD) {
            dom_game_replay_record_view view;
            view.tick = tick;
            view.payload = payload;
            view.size = size;
            records.push_back(view);
        }

        if (!has_last_tick || tick > last_tick) {
            last_tick = tick;
            has_last_tick = 1;
        }

        offset += (size_t)size;
        prev_tick = tick;
        has_prev_tick = 1;
    }

    if (!has_last_tick) {
        last_tick = 0u;
        has_last_tick = 1;
    }

    play = new dom_game_replay_play();
    play->data.swap(data);
    play->records.swap(records);
    play->cursor = 0u;
    play->last_tick = last_tick;
    play->has_last_tick = has_last_tick;
    play->ups = ups;
    play->seed = seed;
    play->feature_epoch = feature_epoch;
    play->content_tlv = content_ptr;
    play->content_tlv_len = content_len;
    play->media_bindings_blob = media_bindings_ptr;
    play->media_bindings_len = media_bindings_len;
    play->media_bindings_version = media_bindings_version;
    play->weather_bindings_blob = weather_bindings_ptr;
    play->weather_bindings_len = weather_bindings_len;
    play->weather_bindings_version = weather_bindings_version;
    play->aero_props_blob = aero_props_ptr;
    play->aero_props_len = aero_props_len;
    play->aero_props_version = aero_props_version;
    play->aero_state_blob = aero_state_ptr;
    play->aero_state_len = aero_state_len;
    play->aero_state_version = aero_state_version;
    play->macro_economy_blob = macro_economy_ptr;
    play->macro_economy_len = macro_economy_len;
    play->macro_economy_version = macro_economy_version;
    play->macro_events_blob = macro_events_ptr;
    play->macro_events_len = macro_events_len;
    play->macro_events_version = macro_events_version;
    play->factions_blob = factions_ptr;
    play->factions_len = factions_len;
    play->factions_version = factions_version;
    play->ai_sched_blob = ai_sched_ptr;
    play->ai_sched_len = ai_sched_len;
    play->ai_sched_version = ai_sched_version;

    if (out_desc) {
        out_desc->container_version = version;
        out_desc->ups = ups;
        out_desc->seed = seed;
        out_desc->feature_epoch = feature_epoch;
        out_desc->instance_id = instance_id;
        out_desc->instance_id_len = instance_id_len;
        out_desc->run_id = run_id_val;
        out_desc->manifest_hash_bytes = manifest_hash;
        out_desc->manifest_hash_len = manifest_hash_len;
        out_desc->content_hash64 = content_hash;
        out_desc->has_identity = (u32)has_identity;
        out_desc->content_tlv = content_ptr;
        out_desc->content_tlv_len = content_len;
        out_desc->media_bindings_blob = media_bindings_ptr;
        out_desc->media_bindings_blob_len = media_bindings_len;
        out_desc->media_bindings_version = media_bindings_version;
        out_desc->has_media_bindings = (u32)has_media_bindings;
        out_desc->weather_bindings_blob = weather_bindings_ptr;
        out_desc->weather_bindings_blob_len = weather_bindings_len;
        out_desc->weather_bindings_version = weather_bindings_version;
        out_desc->has_weather_bindings = (u32)has_weather_bindings;
        out_desc->aero_props_blob = aero_props_ptr;
        out_desc->aero_props_blob_len = aero_props_len;
        out_desc->aero_props_version = aero_props_version;
        out_desc->has_aero_props = (u32)has_aero_props;
        out_desc->aero_state_blob = aero_state_ptr;
        out_desc->aero_state_blob_len = aero_state_len;
        out_desc->aero_state_version = aero_state_version;
        out_desc->has_aero_state = (u32)has_aero_state;
        out_desc->macro_economy_blob = macro_economy_ptr;
        out_desc->macro_economy_blob_len = macro_economy_len;
        out_desc->macro_economy_version = macro_economy_version;
        out_desc->has_macro_economy = (u32)has_macro_economy;
        out_desc->macro_events_blob = macro_events_ptr;
        out_desc->macro_events_blob_len = macro_events_len;
        out_desc->macro_events_version = macro_events_version;
        out_desc->has_macro_events = (u32)has_macro_events;
        out_desc->factions_blob = factions_ptr;
        out_desc->factions_blob_len = factions_len;
        out_desc->factions_version = factions_version;
        out_desc->has_factions = (u32)has_factions;
        out_desc->ai_sched_blob = ai_sched_ptr;
        out_desc->ai_sched_blob_len = ai_sched_len;
        out_desc->ai_sched_version = ai_sched_version;
        out_desc->has_ai_sched = (u32)has_ai_sched;
        out_desc->error_code = DOM_GAME_REPLAY_OK;
    }

    return play;
}

void dom_game_replay_play_close(dom_game_replay_play *play) {
    if (!play) {
        return;
    }
    delete play;
}

int dom_game_replay_play_next_for_tick(dom_game_replay_play *play,
                                       u64 tick,
                                       const dom_game_replay_packet **out_packets,
                                       u32 *out_count) {
    if (!play || !out_packets || !out_count) {
        return DOM_GAME_REPLAY_ERR;
    }

    play->scratch.clear();

    if (play->cursor < play->records.size() &&
        play->records[play->cursor].tick < tick) {
        return DOM_GAME_REPLAY_ERR_FORMAT;
    }

    if (play->cursor >= play->records.size()) {
        *out_packets = (const dom_game_replay_packet *)0;
        *out_count = 0u;
        if (play->has_last_tick && tick > play->last_tick) {
            return DOM_GAME_REPLAY_END;
        }
        return DOM_GAME_REPLAY_OK;
    }

    if (play->records[play->cursor].tick > tick) {
        *out_packets = (const dom_game_replay_packet *)0;
        *out_count = 0u;
        return DOM_GAME_REPLAY_OK;
    }

    while (play->cursor < play->records.size() &&
           play->records[play->cursor].tick == tick) {
        dom_game_replay_packet pkt;
        pkt.payload = play->records[play->cursor].payload;
        pkt.size = play->records[play->cursor].size;
        play->scratch.push_back(pkt);
        play->cursor += 1u;
    }

    if (play->scratch.empty()) {
        *out_packets = (const dom_game_replay_packet *)0;
        *out_count = 0u;
    } else {
        *out_packets = &play->scratch[0];
        *out_count = (u32)play->scratch.size();
    }

    return DOM_GAME_REPLAY_OK;
}

u64 dom_game_replay_play_last_tick(const dom_game_replay_play *play) {
    if (!play || !play->has_last_tick) {
        return 0ull;
    }
    return play->last_tick;
}

} /* extern "C" */
