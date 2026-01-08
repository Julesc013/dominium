/*
FILE: source/dominium/game/runtime/dom_surface_chunks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_chunks
RESPONSIBILITY: Surface chunk keying, lifecycle, and non-blocking request pipeline.
*/
#include "runtime/dom_surface_chunks.h"

#include <algorithm>
#include <vector>
#include <cstring>

#include "runtime/dom_derived_jobs.h"
#include "domino/core/dom_deterministic_math.h"

namespace {

static const u32 DEFAULT_MAX_CHUNKS = 256u;
static const u32 DEFAULT_CHUNK_SIZE_M = 2048u;
static const q16_16 TWO_PI_Q16_16 = (q16_16)411775; /* 2*pi in Q16.16 */

struct SurfaceChunk {
    dom_surface_chunk_key key;
    u32 state;
    u32 generation;
    dom_derived_job_id job_id;
};

struct dom_surface_chunks {
    std::vector<SurfaceChunk> chunks;
    dom_derived_queue *queue;
    u32 max_chunks;
    u32 chunk_size_m;
    u32 generation;
};

struct SurfaceJobPayload {
    dom_derived_job_budget_hint hint;
    dom_surface_chunk_key key;
};

static bool key_less(const dom_surface_chunk_key &a, const dom_surface_chunk_key &b) {
    if (a.body_id != b.body_id) {
        return a.body_id < b.body_id;
    }
    if (a.step_turns_q16 != b.step_turns_q16) {
        return a.step_turns_q16 < b.step_turns_q16;
    }
    if (a.lat_index != b.lat_index) {
        return a.lat_index < b.lat_index;
    }
    return a.lon_index < b.lon_index;
}

static bool key_equal(const dom_surface_chunk_key &a, const dom_surface_chunk_key &b) {
    return a.body_id == b.body_id &&
           a.step_turns_q16 == b.step_turns_q16 &&
           a.lat_index == b.lat_index &&
           a.lon_index == b.lon_index;
}

static bool chunk_less(const SurfaceChunk &a, const SurfaceChunk &b) {
    return key_less(a.key, b.key);
}

static i32 div_floor_i32(i32 num, i32 den) {
    i32 q;
    i32 r;
    if (den == 0) {
        return 0;
    }
    q = num / den;
    r = num % den;
    if (r != 0 && ((r > 0) != (den > 0))) {
        q -= 1;
    }
    return q;
}

static int compute_step_turns_q16(const dom_body_registry *bodies,
                                  dom_body_id body_id,
                                  u32 chunk_size_m,
                                  q16_16 *out_step) {
    dom_body_info info;
    q48_16 radius;
    q48_16 circ;
    q48_16 chunk;
    q48_16 step;
    q16_16 step_q16;

    if (!bodies || !out_step || chunk_size_m == 0u) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    if (dom_body_registry_get(bodies, body_id, &info) != DOM_BODY_REGISTRY_OK) {
        return DOM_SURFACE_CHUNKS_ERR;
    }
    radius = info.radius_m;
    if (radius <= 0) {
        return DOM_SURFACE_CHUNKS_ERR;
    }

    circ = d_q48_16_mul(radius, d_q48_16_from_q16_16(TWO_PI_Q16_16));
    chunk = d_q48_16_from_int((i64)chunk_size_m);
    step = d_q48_16_div(chunk, circ);
    step_q16 = d_q16_16_from_q48_16(step);
    if (step_q16 <= 0) {
        step_q16 = 1;
    }
    *out_step = step_q16;
    return DOM_SURFACE_CHUNKS_OK;
}

static int build_key_from_latlong(const dom_body_registry *bodies,
                                  dom_body_id body_id,
                                  u32 chunk_size_m,
                                  const dom_topo_latlong_q16 *latlong,
                                  dom_surface_chunk_key *out_key) {
    q16_16 step_turns;
    q16_16 lon_norm;
    i32 lat_index;
    i32 lon_index;
    int rc;

    if (!latlong || !out_key) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    rc = compute_step_turns_q16(bodies, body_id, chunk_size_m, &step_turns);
    if (rc != DOM_SURFACE_CHUNKS_OK) {
        return rc;
    }

    lon_norm = dom_angle_normalize_q16(latlong->lon_turns);
    lat_index = div_floor_i32(latlong->lat_turns, step_turns);
    lon_index = (i32)((u32)lon_norm / (u32)step_turns);

    out_key->body_id = body_id;
    out_key->step_turns_q16 = (i32)step_turns;
    out_key->lat_index = lat_index;
    out_key->lon_index = lon_index;
    return DOM_SURFACE_CHUNKS_OK;
}

static SurfaceChunk *find_chunk(dom_surface_chunks *chunks,
                                const dom_surface_chunk_key &key,
                                size_t *out_index) {
    size_t i;
    if (!chunks) {
        return 0;
    }
    for (i = 0u; i < chunks->chunks.size(); ++i) {
        if (key_equal(chunks->chunks[i].key, key)) {
            if (out_index) {
                *out_index = i;
            }
            return &chunks->chunks[i];
        }
    }
    return 0;
}

static void fill_status(const SurfaceChunk &chunk, dom_surface_chunk_status *out_status) {
    if (!out_status) {
        return;
    }
    out_status->key = chunk.key;
    out_status->state = chunk.state;
}

} // namespace

extern "C" {

dom_surface_chunks *dom_surface_chunks_create(const dom_surface_chunks_desc *desc) {
    dom_surface_chunks *chunks;
    dom_derived_queue_desc qdesc;

    if (!desc || desc->struct_size != sizeof(*desc) ||
        desc->struct_version != DOM_SURFACE_CHUNKS_DESC_VERSION) {
        return (dom_surface_chunks *)0;
    }

    chunks = new dom_surface_chunks();
    chunks->chunks.clear();
    chunks->max_chunks = desc->max_chunks ? desc->max_chunks : DEFAULT_MAX_CHUNKS;
    chunks->chunk_size_m = desc->chunk_size_m ? desc->chunk_size_m : DEFAULT_CHUNK_SIZE_M;
    chunks->generation = 1u;

    std::memset(&qdesc, 0, sizeof(qdesc));
    qdesc.struct_size = sizeof(qdesc);
    qdesc.struct_version = DOM_DERIVED_QUEUE_DESC_VERSION;
    qdesc.max_jobs = chunks->max_chunks;
    qdesc.max_payload_bytes = 4096u;
    qdesc.flags = 0u;
    chunks->queue = dom_derived_queue_create(&qdesc);
    if (!chunks->queue) {
        delete chunks;
        return (dom_surface_chunks *)0;
    }
    return chunks;
}

void dom_surface_chunks_destroy(dom_surface_chunks *chunks) {
    if (!chunks) {
        return;
    }
    dom_derived_queue_destroy(chunks->queue);
    delete chunks;
}

int dom_surface_chunk_get_or_create(dom_surface_chunks *chunks,
                                    const dom_surface_chunk_key *key,
                                    dom_surface_chunk_status *out_status) {
    SurfaceChunk entry;
    SurfaceChunk *found;
    size_t idx;

    if (!chunks || !key) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    found = find_chunk(chunks, *key, &idx);
    if (found) {
        fill_status(*found, out_status);
        return DOM_SURFACE_CHUNKS_OK;
    }
    if (chunks->chunks.size() >= chunks->max_chunks) {
        return DOM_SURFACE_CHUNKS_LIMIT;
    }
    std::memset(&entry, 0, sizeof(entry));
    entry.key = *key;
    entry.state = DOM_SURFACE_CHUNK_STATE_INACTIVE;
    entry.generation = 0u;
    entry.job_id = 0u;
    chunks->chunks.push_back(entry);
    std::sort(chunks->chunks.begin(), chunks->chunks.end(), chunk_less);
    found = find_chunk(chunks, *key, 0);
    if (found) {
        fill_status(*found, out_status);
    }
    return DOM_SURFACE_CHUNKS_OK;
}

int dom_surface_chunk_request_load(dom_surface_chunks *chunks,
                                   const dom_surface_chunk_key *key) {
    SurfaceChunk *chunk;
    size_t idx;
    SurfaceJobPayload payload;
    dom_derived_job_payload job_payload;
    dom_derived_job_id job_id;

    if (!chunks || !key) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    chunk = find_chunk(chunks, *key, &idx);
    if (!chunk) {
        return DOM_SURFACE_CHUNKS_ERR;
    }
    if (chunk->state != DOM_SURFACE_CHUNK_STATE_INACTIVE) {
        return DOM_SURFACE_CHUNKS_OK;
    }

    payload.hint.work_ms = 1u;
    payload.hint.io_bytes = 0u;
    payload.key = *key;

    job_payload.data = &payload;
    job_payload.size = sizeof(payload);

    job_id = dom_derived_submit(chunks->queue, DERIVED_BUILD_MAP_TILE, &job_payload, 0);
    if (job_id == 0u) {
        return DOM_SURFACE_CHUNKS_ERR;
    }

    chunk->state = DOM_SURFACE_CHUNK_STATE_REQUESTED;
    chunk->job_id = job_id;
    return DOM_SURFACE_CHUNKS_OK;
}

int dom_surface_chunk_pump_jobs(dom_surface_chunks *chunks,
                                u32 max_ms,
                                u64 max_io_bytes,
                                u32 max_jobs) {
    size_t i;
    if (!chunks) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    (void)dom_derived_pump(chunks->queue, max_ms, max_io_bytes, max_jobs);
    for (i = 0u; i < chunks->chunks.size(); ++i) {
        SurfaceChunk &chunk = chunks->chunks[i];
        if (chunk.job_id == 0u || chunk.state != DOM_SURFACE_CHUNK_STATE_REQUESTED) {
            continue;
        }
        dom_derived_job_status status;
        std::memset(&status, 0, sizeof(status));
        if (dom_derived_poll(chunks->queue, chunk.job_id, &status) != 0) {
            continue;
        }
        if (status.state == DOM_DERIVED_JOB_DONE) {
            chunk.state = DOM_SURFACE_CHUNK_STATE_READY;
            chunk.job_id = 0u;
        } else if (status.state == DOM_DERIVED_JOB_FAILED ||
                   status.state == DOM_DERIVED_JOB_CANCELED) {
            chunk.state = DOM_SURFACE_CHUNK_STATE_ACTIVE;
            chunk.job_id = 0u;
        }
    }
    return DOM_SURFACE_CHUNKS_OK;
}

int dom_surface_chunk_evict(dom_surface_chunks *chunks,
                            u32 max_chunks) {
    size_t i = 0u;
    if (!chunks) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    if (max_chunks == 0u) {
        max_chunks = 1u;
    }
    while (chunks->chunks.size() > max_chunks && i < chunks->chunks.size()) {
        if (chunks->chunks[i].generation != chunks->generation) {
            chunks->chunks.erase(chunks->chunks.begin() + (std::vector<SurfaceChunk>::difference_type)i);
            continue;
        }
        ++i;
    }
    return DOM_SURFACE_CHUNKS_OK;
}

int dom_surface_chunks_build_key(const dom_surface_chunks *chunks,
                                 const dom_body_registry *bodies,
                                 dom_body_id body_id,
                                 const dom_topo_latlong_q16 *latlong,
                                 dom_surface_chunk_key *out_key) {
    if (!chunks || !bodies || !latlong || !out_key) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    return build_key_from_latlong(bodies, body_id, chunks->chunk_size_m, latlong, out_key);
}

int dom_surface_chunks_set_interest(dom_surface_chunks *chunks,
                                    const dom_body_registry *bodies,
                                    dom_body_id body_id,
                                    const dom_topo_latlong_q16 *center,
                                    q48_16 radius_m) {
    dom_surface_chunk_key center_key;
    i32 radius_chunks;
    i32 dx;
    i32 dy;
    int rc;

    if (!chunks || !bodies || !center) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }

    rc = build_key_from_latlong(bodies, body_id, chunks->chunk_size_m, center, &center_key);
    if (rc != DOM_SURFACE_CHUNKS_OK) {
        return rc;
    }

    radius_chunks = (i32)(d_q48_16_to_int(radius_m) / (i64)chunks->chunk_size_m);
    if (radius_chunks < 1) {
        radius_chunks = 1;
    }

    chunks->generation += 1u;
    if (chunks->generation == 0u) {
        chunks->generation = 1u;
    }

    for (dy = -radius_chunks; dy <= radius_chunks; ++dy) {
        for (dx = -radius_chunks; dx <= radius_chunks; ++dx) {
            dom_surface_chunk_key key = center_key;
            dom_surface_chunk_status status;
            SurfaceChunk *chunk;
            key.lat_index = center_key.lat_index + dy;
            key.lon_index = center_key.lon_index + dx;
            rc = dom_surface_chunk_get_or_create(chunks, &key, &status);
            if (rc != DOM_SURFACE_CHUNKS_OK) {
                continue;
            }
            chunk = find_chunk(chunks, key, 0);
            if (chunk) {
                chunk->generation = chunks->generation;
            }
            (void)dom_surface_chunk_request_load(chunks, &key);
        }
    }

    (void)dom_surface_chunk_evict(chunks, chunks->max_chunks);
    return DOM_SURFACE_CHUNKS_OK;
}

int dom_surface_chunks_clear_interest(dom_surface_chunks *chunks) {
    if (!chunks) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    chunks->generation += 1u;
    if (chunks->generation == 0u) {
        chunks->generation = 1u;
    }
    (void)dom_surface_chunk_evict(chunks, chunks->max_chunks);
    return DOM_SURFACE_CHUNKS_OK;
}

int dom_surface_chunks_list_active(dom_surface_chunks *chunks,
                                   dom_surface_chunk_status *out_list,
                                   u32 max_entries,
                                   u32 *out_count) {
    u32 count = 0u;
    size_t i;
    if (!chunks || !out_count) {
        return DOM_SURFACE_CHUNKS_INVALID_ARGUMENT;
    }
    for (i = 0u; i < chunks->chunks.size(); ++i) {
        const SurfaceChunk &chunk = chunks->chunks[i];
        if (chunk.state == DOM_SURFACE_CHUNK_STATE_INACTIVE) {
            continue;
        }
        if (out_list && count < max_entries) {
            out_list[count].key = chunk.key;
            out_list[count].state = chunk.state;
        }
        count += 1u;
    }
    *out_count = count;
    return DOM_SURFACE_CHUNKS_OK;
}

int dom_surface_chunks_has_pending(const dom_surface_chunks *chunks) {
    size_t i;
    if (!chunks) {
        return 0;
    }
    for (i = 0u; i < chunks->chunks.size(); ++i) {
        if (chunks->chunks[i].state == DOM_SURFACE_CHUNK_STATE_REQUESTED) {
            return 1;
        }
    }
    return 0;
}

} /* extern "C" */
