/* Observation buffer (deterministic; C89).
 *
 * Buffers dg_pkt_observation packets for a single observer agent and tick.
 * Storage is bounded: max observations and arena bytes are fixed by reserve().
 *
 * Canonical ordering (authoritative):
 *   (type_id, src_entity, seq) with deterministic tie-breaks.
 */
#ifndef DG_OBSERVATION_BUFFER_H
#define DG_OBSERVATION_BUFFER_H

#include "agent/dg_agent_ids.h"
#include "sim/pkt/dg_pkt_observation.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_observation_record {
    dg_pkt_hdr          hdr;      /* copied */
    const unsigned char *payload; /* points into arena (or NULL) */
    u32                 payload_len;
} dg_observation_record;

typedef struct dg_observation_buffer {
    dg_tick     tick;
    dg_agent_id agent_id; /* observer agent */

    dg_observation_record *records;
    u32                    count;
    u32                    capacity;

    unsigned char *arena;
    u32            arena_cap;
    u32            arena_used;

    d_bool owns_storage;

    u32 probe_refused_records;
    u32 probe_refused_arena;
} dg_observation_buffer;

void dg_observation_buffer_init(dg_observation_buffer *b);
void dg_observation_buffer_free(dg_observation_buffer *b);

/* Allocate bounded storage for the tick buffer. */
int dg_observation_buffer_reserve(dg_observation_buffer *b, u32 max_obs, u32 arena_bytes);

void dg_observation_buffer_begin_tick(dg_observation_buffer *b, dg_tick tick, dg_agent_id agent_id);

/* Push an observation packet. Returns 0 on success; non-zero if refused/invalid. */
int dg_observation_buffer_push(dg_observation_buffer *b, const dg_pkt_observation *obs);

/* Sort records into canonical deterministic order for stable iteration/comparison. */
void dg_observation_buffer_canonize(dg_observation_buffer *b);

u32 dg_observation_buffer_count(const dg_observation_buffer *b);
const dg_observation_record *dg_observation_buffer_at(const dg_observation_buffer *b, u32 index);

u32 dg_observation_buffer_probe_refused_records(const dg_observation_buffer *b);
u32 dg_observation_buffer_probe_refused_arena(const dg_observation_buffer *b);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_OBSERVATION_BUFFER_H */

