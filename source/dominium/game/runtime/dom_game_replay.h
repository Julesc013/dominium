/*
FILE: source/dominium/game/runtime/dom_game_replay.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_replay
RESPONSIBILITY: Defines DMRP replay record/playback helpers; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (recorded command payloads must be stable).
VERSIONING / ABI / DATA FORMAT NOTES: DMRP v1 container; see `source/dominium/game/SPEC_REPLAY.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_REPLAY_V1_H
#define DOM_GAME_REPLAY_V1_H

#ifdef __cplusplus
extern "C" {
#endif
#include "domino/core/types.h"
#ifdef __cplusplus
} /* extern "C" */
#endif

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_GAME_REPLAY_OK = 0,
    DOM_GAME_REPLAY_ERR = -1,
    DOM_GAME_REPLAY_ERR_FORMAT = -2,
    DOM_GAME_REPLAY_ERR_MIGRATION = -3,
    DOM_GAME_REPLAY_END = 1
};

enum {
    DOM_GAME_REPLAY_DESC_VERSION = 1u
};

typedef struct dom_game_replay_record dom_game_replay_record;
typedef struct dom_game_replay_play dom_game_replay_play;

typedef struct dom_game_replay_desc {
    u32 struct_size;
    u32 struct_version;
    u32 container_version;
    u32 ups;
    u64 seed;
    const unsigned char *content_tlv;
    u32 content_tlv_len;
    int error_code;
} dom_game_replay_desc;

typedef struct dom_game_replay_packet {
    const unsigned char *payload;
    u32 size;
} dom_game_replay_packet;

dom_game_replay_record *dom_game_replay_record_open(const char *path,
                                                    u32 ups,
                                                    u64 seed,
                                                    const unsigned char *content_tlv,
                                                    u32 content_tlv_len);
void dom_game_replay_record_close(dom_game_replay_record *rec);
int dom_game_replay_record_write_cmd(dom_game_replay_record *rec,
                                     u64 tick,
                                     const unsigned char *payload,
                                     u32 size);

dom_game_replay_play *dom_game_replay_play_open(const char *path,
                                                dom_game_replay_desc *out_desc);
void dom_game_replay_play_close(dom_game_replay_play *play);
int dom_game_replay_play_next_for_tick(dom_game_replay_play *play,
                                       u64 tick,
                                       const dom_game_replay_packet **out_packets,
                                       u32 *out_count);
u64 dom_game_replay_play_last_tick(const dom_game_replay_play *play);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_GAME_REPLAY_V1_H */
