/*
FILE: source/dominium/game/runtime/dom_game_net_snapshot.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_net_snapshot
RESPONSIBILITY: Defines minimal server-auth snapshot container format (v0).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Serialization is deterministic and uses explicit little-endian encodings.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_NET_SNAPSHOT_H
#define DOM_GAME_NET_SNAPSHOT_H

#include <vector>

extern "C" {
#include "domino/core/types.h"
}

struct dom_game_runtime;

#define DOM_U32_FOURCC(a,b,c,d) \
    ((u32)(a) | ((u32)(b) << 8) | ((u32)(c) << 16) | ((u32)(d) << 24))

enum {
    DOM_NET_SNAPSHOT_OK = 0,
    DOM_NET_SNAPSHOT_ERR = -1,
    DOM_NET_SNAPSHOT_FORMAT = -2
};

enum {
    DOM_GAME_NET_SNAPSHOT_OPTS_VERSION = 1u
};

enum {
    DOM_NET_SNAPSHOT_ASSIST_NONE = 0u,
    DOM_NET_SNAPSHOT_ASSIST_LOCAL_MESH = 1u << 0,
    DOM_NET_SNAPSHOT_ASSIST_LOCAL_CACHE = 1u << 1
};

enum {
    DOM_NET_SNAPSHOT_CHUNK_TIME = DOM_U32_FOURCC('T','I','M','E'),
    DOM_NET_SNAPSHOT_CHUNK_IDEN = DOM_U32_FOURCC('I','D','E','N'),
    DOM_NET_SNAPSHOT_CHUNK_VESL = DOM_U32_FOURCC('V','E','S','L'),
    DOM_NET_SNAPSHOT_CHUNK_SURF = DOM_U32_FOURCC('S','U','R','F')
};

enum {
    DOM_NET_SNAPSHOT_TIME_VERSION = 1u,
    DOM_NET_SNAPSHOT_IDEN_VERSION = 1u,
    DOM_NET_SNAPSHOT_VESL_VERSION = 1u,
    DOM_NET_SNAPSHOT_SURF_VERSION = 1u
};

enum {
    DOM_NET_SNAPSHOT_TLV_UPS = 0x0001u,
    DOM_NET_SNAPSHOT_TLV_TICK = 0x0002u
};

enum {
    DOM_NET_SNAPSHOT_TLV_CONTENT_HASH64 = 0x0001u
};

enum {
    DOM_NET_SNAPSHOT_TLV_VESSEL_COUNT = 0x0001u
};

enum {
    DOM_NET_SNAPSHOT_TLV_SURFACE_COUNT = 0x0001u
};

typedef struct dom_game_net_snapshot_desc {
    u32 ups;
    u64 tick_index;
    u64 content_hash64;
    u32 vessel_count;
    u32 surface_chunk_count;
} dom_game_net_snapshot_desc;

typedef struct dom_game_net_snapshot_opts {
    u32 struct_size;
    u32 struct_version;
    u32 detail_level;
    u32 interest_radius_m;
    u32 assist_flags;
} dom_game_net_snapshot_opts;

int dom_game_net_snapshot_build(const struct dom_game_runtime *rt,
                                const dom_game_net_snapshot_opts *opts,
                                std::vector<unsigned char> &out_bytes);
int dom_game_net_snapshot_parse(const unsigned char *data,
                                size_t len,
                                dom_game_net_snapshot_desc *out_desc);

#endif /* DOM_GAME_NET_SNAPSHOT_H */
