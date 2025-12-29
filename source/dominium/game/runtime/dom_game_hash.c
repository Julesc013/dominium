/*
FILE: source/dominium/game/runtime/dom_game_hash.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_hash
RESPONSIBILITY: Implements deterministic hash helpers for the game runtime; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-critical; hashes must be stable across platforms.
VERSIONING / ABI / DATA FORMAT NOTES: Hash definition must track `docs/SPEC_DETERMINISM.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_game_hash.h"

d_world_hash dom_game_hash_world(const d_world *w) {
    return d_sim_hash_world(w);
}
