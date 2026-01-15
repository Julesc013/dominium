/*
FILE: source/dominium/tools/replay_analyzer/ra_parser.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/replay_analyzer
RESPONSIBILITY: Implements replay parsing and deterministic hashes.
*/
#include "ra_parser.h"

#include <cstring>

namespace dom {
namespace tools {
namespace {

static const u64 FNV_OFFSET = 1469598103934665603ull;
static const u64 FNV_PRIME = 1099511628211ull;

static u64 fnv1a64(const unsigned char *data, size_t len, u64 seed) {
    size_t i;
    u64 h = seed;
    if (!data || len == 0u) {
        return h;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= FNV_PRIME;
    }
    return h;
}

} // namespace

bool ra_parse_replay(const std::string &path,
                     bool capture_ticks,
                     RaReplaySummary &out,
                     std::string *err) {
    dom_game_replay_desc desc;
    dom_game_replay_play *play = 0;
    RaReplaySummary summary;
    u64 last_tick = 0ull;
    u64 total_cmds = 0ull;
    u64 overall_hash = FNV_OFFSET;
    u64 tick;

    if (path.empty()) {
        if (err) *err = "replay_path_empty";
        return false;
    }

    std::memset(&desc, 0, sizeof(desc));
    play = dom_game_replay_play_open(path.c_str(), &desc);
    if (!play) {
        if (err) *err = "replay_open_failed";
        return false;
    }

    last_tick = dom_game_replay_play_last_tick(play);
    summary.last_tick = last_tick;
    summary.total_cmds = 0ull;
    summary.hash64 = FNV_OFFSET;
    summary.ups = desc.ups;
    summary.feature_epoch = desc.feature_epoch;
    summary.run_id = desc.run_id;
    if (desc.instance_id && desc.instance_id_len > 0u) {
        summary.instance_id.assign(desc.instance_id, desc.instance_id_len);
    } else {
        summary.instance_id.clear();
    }
    summary.ticks.clear();

    for (tick = 0ull; tick <= last_tick; ++tick) {
        const dom_game_replay_packet *packets = 0;
        u32 count = 0u;
        int rc = dom_game_replay_play_next_for_tick(play, tick, &packets, &count);
        u64 tick_hash = FNV_OFFSET;
        u32 i;
        if (rc == DOM_GAME_REPLAY_END) {
            break;
        }
        if (rc != DOM_GAME_REPLAY_OK) {
            dom_game_replay_play_close(play);
            if (err) *err = "replay_read_failed";
            return false;
        }
        for (i = 0u; i < count; ++i) {
            const dom_game_replay_packet *p = &packets[i];
            if (!p || !p->payload || p->size == 0u) {
                continue;
            }
            tick_hash = fnv1a64(p->payload, (size_t)p->size, tick_hash);
            overall_hash = fnv1a64(p->payload, (size_t)p->size, overall_hash);
        }
        total_cmds += (u64)count;
        if (capture_ticks) {
            RaTickSummary ts;
            ts.tick = tick;
            ts.cmd_count = count;
            ts.hash64 = tick_hash;
            summary.ticks.push_back(ts);
        }
    }

    summary.total_cmds = total_cmds;
    summary.hash64 = overall_hash;
    out = summary;
    dom_game_replay_play_close(play);
    return true;
}

} // namespace tools
} // namespace dom
