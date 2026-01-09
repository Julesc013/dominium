/*
FILE: source/dominium/game/runtime/dom_game_save.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_save
RESPONSIBILITY: Defines DMSG save/load helpers for the runtime kernel; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (hash comparisons across save/load); see `docs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: DMSG v4 container; see `source/dominium/game/SPEC_SAVE.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_RUNTIME_SAVE_H
#define DOM_GAME_RUNTIME_SAVE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_game_runtime dom_game_runtime;

enum {
    DOM_GAME_SAVE_OK = 0,
    DOM_GAME_SAVE_ERR = -1,
    DOM_GAME_SAVE_ERR_MIGRATION = -2,
    DOM_GAME_SAVE_ERR_FORMAT = -3
};

enum {
    DOM_GAME_SAVE_DESC_VERSION = 9u
};

typedef struct dom_game_save_desc {
    u32 struct_size;
    u32 struct_version;

    u32 container_version;
    u32 ups;
    u64 tick_index;
    u64 seed;
    u32 feature_epoch;

    const char *instance_id;
    u32 instance_id_len;
    u64 run_id;
    const unsigned char *manifest_hash_bytes;
    u32 manifest_hash_len;
    u64 content_hash64;
    u32 has_identity;

    const unsigned char *content_tlv;
    u32 content_tlv_len;

    const unsigned char *core_blob;
    u32 core_blob_len;
    u32 core_version;

    const unsigned char *orbit_blob;
    u32 orbit_blob_len;
    u32 orbit_version;
    u32 has_orbit;

    const unsigned char *surface_blob;
    u32 surface_blob_len;
    u32 surface_version;
    u32 has_surface;

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

    const unsigned char *construction_blob;
    u32 construction_blob_len;
    u32 construction_version;
    u32 has_construction;

    const unsigned char *stations_blob;
    u32 stations_blob_len;
    u32 stations_version;
    u32 has_stations;

    const unsigned char *routes_blob;
    u32 routes_blob_len;
    u32 routes_version;
    u32 has_routes;

    const unsigned char *transfers_blob;
    u32 transfers_blob_len;
    u32 transfers_version;
    u32 has_transfers;

    const unsigned char *production_blob;
    u32 production_blob_len;
    u32 production_version;
    u32 has_production;

    const unsigned char *macro_economy_blob;
    u32 macro_economy_blob_len;
    u32 macro_economy_version;
    u32 has_macro_economy;

    const unsigned char *macro_events_blob;
    u32 macro_events_blob_len;
    u32 macro_events_version;
    u32 has_macro_events;

    u32 rng_state;
    u32 rng_version;
    u32 has_rng;
} dom_game_save_desc;

int dom_game_save_read(const char *path,
                       dom_game_save_desc *out_desc,
                       unsigned char **out_storage,
                       u32 *out_storage_len);

void dom_game_save_release(unsigned char *storage);

int dom_game_save_write(const char *path,
                        const dom_game_runtime *rt,
                        u32 flags);

int dom_game_runtime_save(dom_game_runtime *rt, const char *path);
int dom_game_runtime_load_save(dom_game_runtime *rt, const char *path);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_GAME_RUNTIME_SAVE_H */
