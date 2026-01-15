/*
FILE: source/domino/sim/replay/serialize/save_universe.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/replay/serialize/save_universe
RESPONSIBILITY: Defines internal contract for `save_universe`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SAVE_UNIVERSE_H
#define DOM_SAVE_UNIVERSE_H

#include "core_types.h"
#include "core_rng.h"
#include "core_ids.h"

typedef struct UniverseMeta {
    u32 version;
    u64 universe_seed;
} UniverseMeta;

typedef struct SurfaceMeta {
    u32 version;
    u32 surface_id;
    u64 seed;
    u32 recipe_id;
    RNGState rng_weather;
    RNGState rng_hydro;
    RNGState rng_misc;
} SurfaceMeta;

b32 save_universe_meta(const char *path, const UniverseMeta *meta);
b32 load_universe_meta(const char *path, UniverseMeta *out_meta);

b32 save_surface_meta(const char *path, const SurfaceMeta *meta);
b32 load_surface_meta(const char *path, SurfaceMeta *out_meta);

#endif /* DOM_SAVE_UNIVERSE_H */
