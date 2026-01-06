/*
FILE: source/tests/dom_replay_epoch_test.cpp
MODULE: Dominium Tests
PURPOSE: Validate replay feature_epoch mismatch refusal.
*/
#include <cstdio>
#include <cstring>

#include "dom_feature_epoch.h"
#include "runtime/dom_game_replay.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static void write_u32_le(unsigned char out[4], u32 v) {
    out[0] = (unsigned char)(v & 0xffu);
    out[1] = (unsigned char)((v >> 8u) & 0xffu);
    out[2] = (unsigned char)((v >> 16u) & 0xffu);
    out[3] = (unsigned char)((v >> 24u) & 0xffu);
}

int main() {
    const char *path = "tmp_epoch_replay.dmrp";
    const unsigned char manifest_hash[4] = { 0x01u, 0x02u, 0x03u, 0x04u };
    const unsigned char content_tlv[4] = { 0x05u, 0x06u, 0x07u, 0x08u };
    dom_game_replay_record *rec;
    dom_game_replay_desc desc;
    dom_game_replay_play *play;
    FILE *fh;
    unsigned char buf[4];
    u32 bad_epoch;

    rec = dom_game_replay_record_open(path,
                                      60u,
                                      123u,
                                      "inst1",
                                      42ull,
                                      manifest_hash,
                                      (u32)sizeof(manifest_hash),
                                      content_tlv,
                                      (u32)sizeof(content_tlv));
    if (!rec) {
        return fail("record_open");
    }
    dom_game_replay_record_close(rec);

    bad_epoch = dom::dom_feature_epoch_current() + 1u;
    write_u32_le(buf, bad_epoch);
    fh = std::fopen(path, "r+b");
    if (!fh) {
        std::remove(path);
        return fail("fopen_patch");
    }
    if (std::fseek(fh, 24L, SEEK_SET) != 0) {
        std::fclose(fh);
        std::remove(path);
        return fail("fseek_patch");
    }
    if (std::fwrite(buf, 1u, 4u, fh) != 4u) {
        std::fclose(fh);
        std::remove(path);
        return fail("fwrite_patch");
    }
    std::fclose(fh);

    std::memset(&desc, 0, sizeof(desc));
    play = dom_game_replay_play_open(path, &desc);
    if (play) {
        dom_game_replay_play_close(play);
        std::remove(path);
        return fail("expected_migration_refusal");
    }
    if (desc.error_code != DOM_GAME_REPLAY_ERR_MIGRATION) {
        std::remove(path);
        return fail("wrong_refusal_code");
    }

    std::remove(path);
    std::printf("dom_replay_epoch_test: OK\n");
    return 0;
}
