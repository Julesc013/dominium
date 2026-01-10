/*
FILE: source/tests/dom_replay_analyzer_basic_test.cpp
MODULE: Dominium Tests
PURPOSE: Ensure replay analyzer parses replays and desync hints deterministically.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "dominium/core_tlv.h"
#include "runtime/dom_game_replay.h"
#include "replay_analyzer/ra_parser.h"
#include "replay_analyzer/ra_diff.h"

namespace {

enum {
    DESYNC_TLV_VERSION = 1u,
    DESYNC_TAG_TICK = 2u,
    DESYNC_TAG_EXPECTED_HASH = 3u,
    DESYNC_TAG_ACTUAL_HASH = 4u
};

static bool write_bytes(const std::string &path, const std::vector<unsigned char> &bytes) {
    FILE *f = std::fopen(path.c_str(), "wb");
    size_t wrote = 0u;
    if (!f) {
        return false;
    }
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    return wrote == bytes.size();
}

static bool write_desync(const std::string &path, u64 tick, u64 expected, u64 actual) {
    dom::core_tlv::TlvWriter w;
    w.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DESYNC_TLV_VERSION);
    w.add_u64(DESYNC_TAG_TICK, tick);
    w.add_u64(DESYNC_TAG_EXPECTED_HASH, expected);
    w.add_u64(DESYNC_TAG_ACTUAL_HASH, actual);
    return write_bytes(path, w.bytes());
}

} // namespace

int main() {
    const char *replay_path = "tmp_replay_analyzer.dmrp";
    const char *desync_path = "tmp_replay_analyzer_desync.tlv";
    dom_game_replay_record *rec = 0;
    std::vector<unsigned char> payload;
    dom::tools::RaReplaySummary summary;
    dom::tools::RaDesyncInfo desync;
    std::string err;
    u64 tick = 0ull;
    u64 hash = 0ull;

    rec = dom_game_replay_record_open(replay_path,
                                      60u,
                                      1ull,
                                      "inst",
                                      99ull,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u);
    assert(rec);

    payload.push_back(0x42u);
    assert(dom_game_replay_record_write_cmd(rec, 2u, &payload[0], (u32)payload.size()) == DOM_GAME_REPLAY_OK);
    dom_game_replay_record_close(rec);

    assert(dom::tools::ra_parse_replay(replay_path, true, summary, &err));
    assert(summary.ups == 60u);
    assert(summary.total_cmds == 1ull);
    assert(summary.last_tick >= 2ull);

    assert(write_desync(desync_path, 2ull, 0x10ull, 0x20ull));
    assert(dom::tools::ra_load_desync(desync_path, desync, &err));
    assert(dom::tools::ra_compare_desync(summary, desync, tick, hash, &err));
    assert(tick == 2ull);
    assert(!summary.ticks.empty());
    assert(hash == summary.ticks[0].hash64);

    std::remove(replay_path);
    std::remove(desync_path);

    std::printf("dom_replay_analyzer_basic_test: OK\n");
    return 0;
}
