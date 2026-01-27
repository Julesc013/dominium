/*
FILE: source/domino/world/d_world.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/d_world
RESPONSIBILITY: Defines internal contract for `d_world`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* World core definitions (C89). */
#ifndef D_WORLD_H
#define D_WORLD_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "domino/core/dom_time_core.h"
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

typedef struct d_macro_capsule_entry {
    u64 capsule_id;
    u64 domain_id;
    dom_act_time_t source_tick;
    unsigned char* bytes;
    u32 byte_count;
    u32 capacity;
    u32 in_use;
} d_macro_capsule_entry;

typedef struct d_macro_schedule_entry {
    u64 domain_id;
    u64 capsule_id;
    dom_act_time_t last_event_time;
    dom_act_time_t next_event_time;
    dom_act_time_t interval_ticks;
    u64 order_key_seed;
    u32 executed_events;
    u32 narrative_events;
    dom_act_time_t compacted_through_time;
    u32 compaction_count;
    u32 in_use;
} d_macro_schedule_entry;

typedef struct d_macro_event_entry {
    u64 event_id;
    u64 domain_id;
    u64 capsule_id;
    dom_act_time_t event_time;
    u64 order_key;
    u64 sequence;
    u32 event_kind;
    u32 flags;
    u32 payload0;
    u32 payload1;
    u32 in_use;
} d_macro_event_entry;

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

    /* Macro capsule save chunks (sorted by capsule_id). */
    d_macro_capsule_entry* macro_capsules;
    u32 macro_capsule_count;
    u32 macro_capsule_capacity;

    /* Macro schedule store (sorted by domain_id). */
    d_macro_schedule_entry* macro_schedules;
    u32 macro_schedule_count;
    u32 macro_schedule_capacity;

    /* Macro event queue (sorted by deterministic ordering key). */
    d_macro_event_entry* macro_events;
    u32 macro_event_count;
    u32 macro_event_capacity;
    u64 macro_event_sequence;

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
