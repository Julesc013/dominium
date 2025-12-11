/* World core definitions (C89). */
#ifndef D_WORLD_H
#define D_WORLD_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "domino/core/rng.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_world_meta {
    u64   seed;
    u32   world_size_m;      /* e.g. 1 << 24 */
    q16_16 vertical_min;     /* e.g. -2000m */
    q16_16 vertical_max;     /* e.g. +2000m */
    u32   core_version;
    u32   suite_version;
    u32   compat_profile_id;
    d_tlv_blob extra;        /* future metadata */
} d_world_meta;

typedef struct d_chunk {
    u32  chunk_id;
    i32  cx;
    i32  cy;
    u16  flags;
    /* Subsystems can attach their own per-chunk indices via their internal tables. */
} d_chunk;

typedef struct d_world {
    d_world_meta meta;

    /* Chunk table / map – simple growable array for now. */
    d_chunk *chunks;
    u32      chunk_count;
    u32      chunk_capacity;

    /* Internal: seed used for worldgen providers etc. */
    u64      worldgen_seed;

    /* Legacy grid state for the existing tile simulation. */
    u32      width;
    u32      height;
    d_rng_state rng;
    u32      tick_count;
    u16     *tile_type;
    q24_8   *tile_height;

    /* TODO: add spatial indexing, chunk lookup tables, etc. */
} d_world;

/* World lifecycle APIs */
d_world *d_world_create(const d_world_meta *meta);
void     d_world_destroy(d_world *w);

/* Chunk management APIs */
d_chunk *d_world_get_or_create_chunk(d_world *w, i32 cx, i32 cy);
d_chunk *d_world_find_chunk(d_world *w, i32 cx, i32 cy);

/* Called when a chunk is first created/generator invoked */
int      d_world_generate_chunk(d_world *w, d_chunk *chunk);

#ifdef __cplusplus
}
#endif

#endif /* D_WORLD_H */
