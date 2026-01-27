/*
FILE: source/domino/world/d_world.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/d_world
RESPONSIBILITY: Implements `d_world`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "d_world.h"
#include "core/d_subsystem.h"
#include "d_worldgen.h"
#include "scale/d_macro_capsule_store.h"
#include "scale/d_macro_schedule_store.h"
#include "scale/d_macro_event_queue_store.h"

/* Forward declaration; implemented in core subsystem init. */
void d_subsystems_init(void);

static int d_world_reserve_chunks(d_world *w, u32 capacity) {
    d_chunk *new_chunks;
    u32 old_cap;
    if (!w) {
        return -1;
    }
    if (capacity <= w->chunk_capacity) {
        return 0;
    }
    new_chunks = (d_chunk *)realloc(w->chunks, capacity * sizeof(d_chunk));
    if (!new_chunks) {
        return -1;
    }
    old_cap = w->chunk_capacity;
    w->chunks = new_chunks;
    w->chunk_capacity = capacity;
    if (w->chunk_capacity > old_cap) {
        u32 i;
        for (i = old_cap; i < w->chunk_capacity; ++i) {
            memset(&w->chunks[i], 0, sizeof(d_chunk));
        }
    }
    return 0;
}

static void d_world_call_init_instance(d_world *w) {
    u32 i;
    u32 count;
    if (!w) {
        return;
    }
    count = d_subsystem_count();
    for (i = 0u; i < count; ++i) {
        const d_subsystem_desc *desc = d_subsystem_get_by_index(i);
        if (desc && desc->init_instance) {
            desc->init_instance(w);
        }
    }
}

d_world *d_world_create(const d_world_meta *meta) {
    d_world *w;
    if (!meta) {
        return (d_world *)0;
    }

    d_subsystems_init();

    w = (d_world *)malloc(sizeof(d_world));
    if (!w) {
        return (d_world *)0;
    }
    memset(w, 0, sizeof(*w));

    w->meta = *meta;
    w->worldgen_seed = meta->seed;
    w->chunks = (d_chunk *)0;
    w->chunk_count = 0u;
    w->chunk_capacity = 0u;
    w->width = 0u;
    w->height = 0u;
    w->tick_count = 0u;
    w->tile_type = (u16 *)0;
    w->tile_height = (q24_8 *)0;
    w->macro_capsules = (d_macro_capsule_entry*)0;
    w->macro_capsule_count = 0u;
    w->macro_capsule_capacity = 0u;
    w->macro_schedules = (d_macro_schedule_entry*)0;
    w->macro_schedule_count = 0u;
    w->macro_schedule_capacity = 0u;
    w->macro_events = (d_macro_event_entry*)0;
    w->macro_event_count = 0u;
    w->macro_event_capacity = 0u;
    w->macro_event_sequence = 0u;
    d_rng_seed(&w->rng, w->worldgen_seed);

    if (d_world_reserve_chunks(w, 8u) != 0) {
        free(w);
        return (d_world *)0;
    }

    d_world_call_init_instance(w);

    return w;
}

void d_world_destroy(d_world *w) {
    if (!w) {
        return;
    }
    d_macro_event_queue_store_free(w);
    d_macro_schedule_store_free(w);
    d_macro_capsule_store_free(w);
    if (w->tile_type) {
        free(w->tile_type);
        w->tile_type = (u16 *)0;
    }
    if (w->tile_height) {
        free(w->tile_height);
        w->tile_height = (q24_8 *)0;
    }
    if (w->chunks) {
        free(w->chunks);
        w->chunks = (d_chunk *)0;
    }
    free(w);
}

d_chunk *d_world_find_chunk(d_world *w, i32 cx, i32 cy) {
    u32 i;
    if (!w || !w->chunks) {
        return (d_chunk *)0;
    }
    for (i = 0u; i < w->chunk_count; ++i) {
        if (w->chunks[i].cx == cx && w->chunks[i].cy == cy) {
            return &w->chunks[i];
        }
    }
    return (d_chunk *)0;
}

d_chunk *d_world_get_or_create_chunk(d_world *w, i32 cx, i32 cy) {
    d_chunk *chunk;
    u32 new_id;
    u32 new_cap;
    int rc;
    if (!w) {
        return (d_chunk *)0;
    }

    chunk = d_world_find_chunk(w, cx, cy);
    if (chunk) {
        return chunk;
    }

    if (w->chunk_count == 0xFFFFFFFFu) {
        return (d_chunk *)0;
    }
    if (w->chunk_count >= w->chunk_capacity) {
        new_cap = w->chunk_capacity ? (w->chunk_capacity * 2u) : 8u;
        rc = d_world_reserve_chunks(w, new_cap);
        if (rc != 0) {
            return (d_chunk *)0;
        }
    }

    chunk = &w->chunks[w->chunk_count];
    memset(chunk, 0, sizeof(*chunk));
    new_id = w->chunk_count + 1u;
    chunk->chunk_id = new_id;
    chunk->cx = cx;
    chunk->cy = cy;
    chunk->flags = 0u;
    w->chunk_count += 1u;

    rc = d_world_generate_chunk(w, chunk);
    if (rc != 0) {
        w->chunk_count -= 1u;
        memset(chunk, 0, sizeof(*chunk));
        return (d_chunk *)0;
    }

    return chunk;
}

int d_world_generate_chunk(d_world *w, d_chunk *chunk) {
    if (!w || !chunk) {
        return -1;
    }
    return d_worldgen_run(w, chunk);
}
