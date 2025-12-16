/*
FILE: source/dominium/game/dom_game_save.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_save
RESPONSIBILITY: Implements `dom_game_save`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_SAVE_H
#define DOM_GAME_SAVE_H

#include <string>
#include <vector>

extern "C" {
#include "world/d_world.h"
#include "world/d_serialize.h"
}

namespace dom {

bool game_save_world(
    d_world             *world,
    const std::string   &path
);

bool game_load_world(
    d_world             *world,
    const std::string   &path
);

/* In-memory save/load helpers for snapshotting. */
bool game_save_world_blob(
    d_world                       *world,
    std::vector<unsigned char>    &out
);

bool game_load_world_blob(
    d_world                  *world,
    const unsigned char      *data,
    size_t                    size
);

} // namespace dom

#endif
