/*
FILE: source/dominium/game/dom_game_replay.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_replay
RESPONSIBILITY: Implements `dom_game_replay`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_REPLAY_H
#define DOM_GAME_REPLAY_H

#include <string>

extern "C" {
#include "replay/d_replay.h"
}

namespace dom {

bool game_save_replay(const d_replay_context *ctx, const std::string &path);
bool game_load_replay(const std::string &path, d_replay_context *out_ctx);
u32  game_replay_last_tick(const d_replay_context *ctx);

} // namespace dom

#endif

