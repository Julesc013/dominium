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
VERSIONING / ABI / DATA FORMAT NOTES: DMRP v4 container; see `source/dominium/game/SPEC_REPLAY.md`.
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
    DOM_GAME_REPLAY_DESC_VERSION = 7u
};

typedef struct dom_game_replay_record dom_game_replay_record;
typedef struct dom_game_replay_play dom_game_replay_play;

typedef struct dom_game_replay_desc {
    u32 struct_size;
    u32 struct_version;
    u32 container_version;
    u32 ups;
    u64 seed;
    u32 feature_epoch;
    const char *instance_id;
    u32 instance_id_len;
    u64 run_id;
    const unsigned char *manifest_hash_bytes;
    u32 manifest_hash_len;
    u64 content_hash64;
    u64 coredata_sim_hash64;
    u32 has_coredata_sim_hash;
    u32 has_identity;
    const unsigned char *content_tlv;
    u32 content_tlv_len;
    const unsigned char *media_bindings_blob;
    u32 media_bindings_blob_len;
    u32 media_bindings_version;
    u32 has_media_bindings;
    const unsigned char *weather_bindings_blob;
    u32 weather_bindings_blob_len;
    u32 weather_bindings_version;
    u32 has_weather_bindings;
    const unsigned char *aero_props_blob;
    u32 aero_props_blob_len;
    u32 aero_props_version;
    u32 has_aero_props;
    const unsigned char *aero_state_blob;
    u32 aero_state_blob_len;
    u32 aero_state_version;
    u32 has_aero_state;
    const unsigned char *macro_economy_blob;
    u32 macro_economy_blob_len;
    u32 macro_economy_version;
    u32 has_macro_economy;
    const unsigned char *macro_events_blob;
    u32 macro_events_blob_len;
    u32 macro_events_version;
    u32 has_macro_events;
    const unsigned char *factions_blob;
    u32 factions_blob_len;
    u32 factions_version;
    u32 has_factions;
    const unsigned char *ai_sched_blob;
    u32 ai_sched_blob_len;
    u32 ai_sched_version;
    u32 has_ai_sched;
    int error_code;
} dom_game_replay_desc;

typedef struct dom_game_replay_packet {
    const unsigned char *payload;
    u32 size;
} dom_game_replay_packet;

dom_game_replay_record *dom_game_replay_record_open(const char *path,
                                                    u32 ups,
                                                    u64 seed,
                                                    const char *instance_id,
                                                    u64 run_id,
                                                    const unsigned char *manifest_hash_bytes,
                                                    u32 manifest_hash_len,
                                                    const unsigned char *content_tlv,
                                                    u32 content_tlv_len,
                                                    u64 coredata_sim_hash,
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
                                                    u32 ai_sched_len);
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
