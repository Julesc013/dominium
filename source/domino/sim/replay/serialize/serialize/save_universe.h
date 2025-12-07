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
