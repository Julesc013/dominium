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
VERSIONING / ABI / DATA FORMAT NOTES: DMRP v1 container; see `source/dominium/game/SPEC_REPLAY.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_replay.h"

#include <vector>
#include <cstring>

extern "C" {
#include "domino/sys.h"
#include "net/d_net_proto.h"
}

namespace {

enum {
    DMRP_VERSION = 1u,
    DMRP_ENDIAN = 0x0000FFFEu
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
    const unsigned char *content_tlv;
    u32 content_tlv_len;
};

extern "C" {

dom_game_replay_record *dom_game_replay_record_open(const char *path,
                                                    u32 ups,
                                                    u64 seed,
                                                    const unsigned char *content_tlv,
                                                    u32 content_tlv_len) {
    dom_game_replay_record *rec;
    unsigned char buf32[4];
    unsigned char buf64[8];
    void *fh;

    if (!path || !path[0] || ups == 0u) {
        return (dom_game_replay_record *)0;
    }
    if (content_tlv_len > 0u && !content_tlv) {
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
    u32 content_len;
    const unsigned char *content_ptr;
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
            out_desc->error_code = (version > DMRP_VERSION) ? DOM_GAME_REPLAY_ERR_MIGRATION
                                                            : DOM_GAME_REPLAY_ERR_FORMAT;
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
    content_len = read_u32_le(&data[24]);

    offset = 28u;
    if ((size_t)content_len > data_len - offset) {
        if (out_desc) {
            out_desc->error_code = DOM_GAME_REPLAY_ERR_FORMAT;
        }
        return (dom_game_replay_play *)0;
    }
    content_ptr = (content_len > 0u) ? (&data[offset]) : (const unsigned char *)0;
    offset += (size_t)content_len;

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
    play->content_tlv = content_ptr;
    play->content_tlv_len = content_len;

    if (out_desc) {
        out_desc->container_version = version;
        out_desc->ups = ups;
        out_desc->seed = seed;
        out_desc->content_tlv = content_ptr;
        out_desc->content_tlv_len = content_len;
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
