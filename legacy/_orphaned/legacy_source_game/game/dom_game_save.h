/*
FILE: source/dominium/game/dom_game_save.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_save
RESPONSIBILITY: Defines internal contract for `dom_game_save`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (save verification compares `d_sim_hash_world`); see `docs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: Legacy, unversioned save blob format; see `docs/DATA_FORMATS.md` (Legacy game save blob).
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

/* game_save_world
 * Purpose: Serialize `world` to `path` using the legacy game save blob format.
 * Parameters:
 *   world: Target world (non-NULL).
 *   path: Output path (non-empty).
 * Return values / errors:
 *   true on success; false on serialization/I/O/verification failure.
 * Side effects:
 *   Writes to disk and may print verification mismatches to stdout.
 */
bool game_save_world(
    d_world             *world,
    const std::string   &path
);

/* game_load_world
 * Purpose: Load `world` from `path` using the legacy game save blob format.
 * Parameters:
 *   world: Target world to populate (non-NULL).
 *   path: Input path (non-empty).
 * Return values / errors:
 *   true on success; false on parse/validation/I/O failure.
 */
bool game_load_world(
    d_world             *world,
    const std::string   &path
);

/* In-memory save/load helpers for snapshotting. */
/* game_save_world_blob
 * Purpose: Serialize `world` into an in-memory legacy blob.
 * Parameters:
 *   world: Target world (non-NULL).
 *   out: Output buffer; overwritten on success.
 * Return values / errors:
 *   true on success; false on serialization failure.
 */
bool game_save_world_blob(
    d_world                       *world,
    std::vector<unsigned char>    &out
);

/* game_load_world_blob
 * Purpose: Load `world` from an in-memory legacy blob.
 * Parameters:
 *   world: Target world to populate (non-NULL).
 *   data/size: Blob bytes. `data` may be NULL only when `size == 0`.
 * Return values / errors:
 *   true on success; false on parse/validation failure.
 */
bool game_load_world_blob(
    d_world                  *world,
    const unsigned char      *data,
    size_t                    size
);

} // namespace dom

#endif
