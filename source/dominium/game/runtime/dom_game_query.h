/*
FILE: source/dominium/game/runtime/dom_game_query.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_query
RESPONSIBILITY: Defines internal runtime query payloads for the game runtime; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal struct versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_QUERY_H
#define DOM_GAME_QUERY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_GAME_QUERY_VERSION = 1u
};

enum {
    DOM_GAME_QUERY_COSMO_MAP = 1u,
    DOM_GAME_QUERY_ACTIVE_TRANSIT = 2u,
    DOM_GAME_QUERY_SYSTEM_LIST = 3u,
    DOM_GAME_QUERY_BODY_LIST = 4u,
    DOM_GAME_QUERY_FRAME_TREE = 5u,
    DOM_GAME_QUERY_BODY_TOPOLOGY_INFO = 6u
};

typedef struct dom_game_counts {
    u32 struct_size;
    u32 struct_version;
    u32 entity_count;
    u32 construction_count;
} dom_game_counts;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_GAME_QUERY_H */
