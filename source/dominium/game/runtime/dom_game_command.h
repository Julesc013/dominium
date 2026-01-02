/*
FILE: source/dominium/game/runtime/dom_game_command.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_command
RESPONSIBILITY: Defines internal command payloads for the game runtime; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal struct versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_COMMAND_H
#define DOM_GAME_COMMAND_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_GAME_COMMAND_VERSION = 1u
};

typedef struct dom_game_command {
    u32 struct_size;
    u32 struct_version;

    /* 0 means "schedule at next tick". */
    u32 tick;

    u32 schema_id;
    u16 schema_ver;
    u16 _pad0;

    const void *payload;
    u32         payload_size;
} dom_game_command;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_GAME_COMMAND_H */
