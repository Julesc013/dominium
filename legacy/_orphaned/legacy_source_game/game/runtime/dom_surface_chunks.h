/*
FILE: source/dominium/game/runtime/dom_surface_chunks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_chunks
RESPONSIBILITY: Surface chunk keying, lifecycle, and non-blocking request pipeline.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_SURFACE_CHUNKS_H
#define DOM_SURFACE_CHUNKS_H

#include "domino/core/fixed.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_surface_topology.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_SURFACE_CHUNKS_OK = 0,
    DOM_SURFACE_CHUNKS_ERR = -1,
    DOM_SURFACE_CHUNKS_INVALID_ARGUMENT = -2,
    DOM_SURFACE_CHUNKS_LIMIT = -3
};

enum {
    DOM_SURFACE_CHUNK_STATE_INACTIVE = 0,
    DOM_SURFACE_CHUNK_STATE_REQUESTED = 1,
    DOM_SURFACE_CHUNK_STATE_ACTIVE = 2,
    DOM_SURFACE_CHUNK_STATE_READY = 3
};

typedef struct dom_surface_chunk_key {
    dom_body_id body_id;
    i32 step_turns_q16;
    i32 lat_index;
    i32 lon_index;
} dom_surface_chunk_key;

typedef struct dom_surface_chunk_status {
    dom_surface_chunk_key key;
    u32 state;
} dom_surface_chunk_status;

enum {
    DOM_SURFACE_CHUNKS_DESC_VERSION = 1u
};

typedef struct dom_surface_chunks_desc {
    u32 struct_size;
    u32 struct_version;
    u32 max_chunks;
    u32 chunk_size_m;
} dom_surface_chunks_desc;

typedef struct dom_surface_chunks dom_surface_chunks;

dom_surface_chunks *dom_surface_chunks_create(const dom_surface_chunks_desc *desc);
void dom_surface_chunks_destroy(dom_surface_chunks *chunks);

int dom_surface_chunk_get_or_create(dom_surface_chunks *chunks,
                                    const dom_surface_chunk_key *key,
                                    dom_surface_chunk_status *out_status);
int dom_surface_chunk_request_load(dom_surface_chunks *chunks,
                                   const dom_surface_chunk_key *key);
int dom_surface_chunk_pump_jobs(dom_surface_chunks *chunks,
                                u32 max_ms,
                                u64 max_io_bytes,
                                u32 max_jobs);
int dom_surface_chunk_evict(dom_surface_chunks *chunks,
                            u32 max_chunks);
int dom_surface_chunks_build_key(const dom_surface_chunks *chunks,
                                 const dom_body_registry *bodies,
                                 dom_body_id body_id,
                                 const dom_topo_latlong_q16 *latlong,
                                 dom_surface_chunk_key *out_key);

int dom_surface_chunks_set_interest(dom_surface_chunks *chunks,
                                    const dom_body_registry *bodies,
                                    dom_body_id body_id,
                                    const dom_topo_latlong_q16 *center,
                                    q48_16 radius_m);
int dom_surface_chunks_clear_interest(dom_surface_chunks *chunks);

int dom_surface_chunks_list_active(dom_surface_chunks *chunks,
                                   dom_surface_chunk_status *out_list,
                                   u32 max_entries,
                                   u32 *out_count);
int dom_surface_chunks_has_pending(const dom_surface_chunks *chunks);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SURFACE_CHUNKS_H */
