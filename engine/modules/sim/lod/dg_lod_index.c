/*
FILE: source/domino/sim/lod/dg_lod_index.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_lod_index
RESPONSIBILITY: Implements `dg_lod_index`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "sim/lod/dg_lod_index.h"

#include "core/det_invariants.h"

/* Quantize stored positions to deterministic quanta (q16_16).
 * 1/16m resolution by default (power-of-two shift).
 */
#define DG_LOD_POS_QUANT_RSHIFT 12u

static q16_16 dg_lod_quantize_q16_16(q16_16 v) {
    i32 raw = (i32)v;
    i32 q = D_DET_RSHIFT_NEAR_I32(raw, DG_LOD_POS_QUANT_RSHIFT);
    return (q16_16)(q << DG_LOD_POS_QUANT_RSHIFT);
}

static dg_lod_obj_pos dg_lod_quantize_pos(dg_lod_obj_pos p) {
    p.x = dg_lod_quantize_q16_16(p.x);
    p.y = dg_lod_quantize_q16_16(p.y);
    p.z = dg_lod_quantize_q16_16(p.z);
    return p;
}

static int dg_lod_cmp_u64(u64 a, u64 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int dg_lod_entry_cmp_fields(
    dg_chunk_id chunk_id,
    dg_lod_class_id class_id,
    dg_domain_id domain_id,
    dg_entity_id entity_id,
    u64 sub_id,
    const dg_lod_index_entry *e
) {
    int c;
    if (!e) return 1;
    c = dg_lod_cmp_u64((u64)chunk_id, (u64)e->chunk_id);
    if (c) return c;
    c = dg_lod_cmp_u64((u64)class_id, (u64)e->class_id);
    if (c) return c;
    c = dg_lod_cmp_u64((u64)domain_id, (u64)e->key.domain_id);
    if (c) return c;
    c = dg_lod_cmp_u64((u64)entity_id, (u64)e->key.entity_id);
    if (c) return c;
    c = dg_lod_cmp_u64(sub_id, e->key.sub_id);
    if (c) return c;
    return 0;
}

static u32 dg_lod_lower_bound(const dg_lod_index *idx, dg_chunk_id chunk_id, dg_lod_class_id class_id, const dg_lod_obj_key *key) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        {
            const dg_lod_index_entry *e = &idx->entries[mid];
            int c = dg_lod_entry_cmp_fields(chunk_id, class_id, key ? key->domain_id : 0u, key ? key->entity_id : 0u, key ? key->sub_id : 0u, e);
            if (c <= 0) {
                hi = mid;
            } else {
                lo = mid + 1u;
            }
        }
    }
    return lo;
}

static u32 dg_lod_lower_bound_chunk(const dg_lod_index *idx, dg_chunk_id chunk_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (idx->entries[mid].chunk_id >= chunk_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 dg_lod_lower_bound_chunk_class(const dg_lod_index *idx, dg_chunk_id chunk_id, dg_lod_class_id class_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        {
            const dg_lod_index_entry *e = &idx->entries[mid];
            if (e->chunk_id > chunk_id) {
                hi = mid;
            } else if (e->chunk_id < chunk_id) {
                lo = mid + 1u;
            } else {
                if (e->class_id >= class_id) {
                    hi = mid;
                } else {
                    lo = mid + 1u;
                }
            }
        }
    }
    return lo;
}

void dg_lod_index_init(dg_lod_index *idx) {
    if (!idx) {
        return;
    }
    memset(idx, 0, sizeof(*idx));
}

void dg_lod_index_free(dg_lod_index *idx) {
    if (!idx) {
        return;
    }
    if (idx->owns_storage && idx->entries) {
        free(idx->entries);
    }
    dg_lod_index_init(idx);
}

int dg_lod_index_reserve(dg_lod_index *idx, u32 capacity) {
    dg_lod_index_entry *e;
    if (!idx) {
        return -1;
    }
    dg_lod_index_free(idx);
    if (capacity == 0u) {
        return 0;
    }
    e = (dg_lod_index_entry *)malloc(sizeof(dg_lod_index_entry) * (size_t)capacity);
    if (!e) {
        return -2;
    }
    memset(e, 0, sizeof(dg_lod_index_entry) * (size_t)capacity);
    idx->entries = e;
    idx->capacity = capacity;
    idx->count = 0u;
    idx->owns_storage = D_TRUE;
    idx->probe_refused = 0u;
    return 0;
}

void dg_lod_index_clear(dg_lod_index *idx) {
    if (!idx) {
        return;
    }
    idx->count = 0u;
}

u32 dg_lod_index_count(const dg_lod_index *idx) {
    return idx ? idx->count : 0u;
}

u32 dg_lod_index_capacity(const dg_lod_index *idx) {
    return idx ? idx->capacity : 0u;
}

u32 dg_lod_index_probe_refused(const dg_lod_index *idx) {
    return idx ? idx->probe_refused : 0u;
}

int dg_lod_index_add(
    dg_lod_index         *idx,
    dg_chunk_id           chunk_id,
    const dg_lod_obj_key *obj_key,
    const dg_lod_obj_pos *obj_pos,
    dg_lod_class_id       class_id
) {
    u32 pos;
    dg_lod_index_entry *e;
    dg_lod_obj_pos qp;

    if (!idx || !idx->entries || idx->capacity == 0u) {
        return -1;
    }
    if (!obj_key || !obj_pos) {
        return -2;
    }
    if (chunk_id == 0u) {
        return -3;
    }
    if (obj_key->chunk_id != 0u && obj_key->chunk_id != chunk_id) {
        return -4;
    }

    qp = *obj_pos;
    qp = dg_lod_quantize_pos(qp);

    pos = dg_lod_lower_bound(idx, chunk_id, class_id, obj_key);
    if (pos < idx->count) {
        e = &idx->entries[pos];
        if (dg_lod_entry_cmp_fields(chunk_id, class_id, obj_key->domain_id, obj_key->entity_id, obj_key->sub_id, e) == 0) {
            /* Update in place. */
            e->pos = qp;
            return 1;
        }
    }

    if (idx->count >= idx->capacity) {
        idx->probe_refused += 1u;
        return -5;
    }

    if (pos < idx->count) {
        memmove(&idx->entries[pos + 1u], &idx->entries[pos],
                sizeof(dg_lod_index_entry) * (size_t)(idx->count - pos));
    }

    e = &idx->entries[pos];
    memset(e, 0, sizeof(*e));
    e->chunk_id = chunk_id;
    e->class_id = class_id;
    e->key = *obj_key;
    e->key.chunk_id = chunk_id;
    e->pos = qp;
    idx->count += 1u;
    return 0;
}

int dg_lod_index_remove(
    dg_lod_index         *idx,
    dg_chunk_id           chunk_id,
    const dg_lod_obj_key *obj_key,
    dg_lod_class_id       class_id
) {
    u32 pos;

    if (!idx || !idx->entries) {
        return -1;
    }
    if (!obj_key) {
        return -2;
    }
    if (chunk_id == 0u) {
        return -3;
    }

    pos = dg_lod_lower_bound(idx, chunk_id, class_id, obj_key);
    if (pos >= idx->count) {
        return 1;
    }
    if (dg_lod_entry_cmp_fields(chunk_id, class_id, obj_key->domain_id, obj_key->entity_id, obj_key->sub_id, &idx->entries[pos]) != 0) {
        return 1;
    }

    if (pos + 1u < idx->count) {
        memmove(&idx->entries[pos], &idx->entries[pos + 1u],
                sizeof(dg_lod_index_entry) * (size_t)(idx->count - (pos + 1u)));
    }
    idx->count -= 1u;
    return 0;
}

u32 dg_lod_index_query(
    const dg_lod_index *idx,
    dg_chunk_id         chunk_id,
    dg_lod_class_id     class_id,
    dg_lod_candidate   *out_candidates,
    u32                 max_out
) {
    u32 written = 0u;
    u32 i;
    u32 start;

    if (!idx || !idx->entries || max_out == 0u || !out_candidates) {
        return 0u;
    }
    if (chunk_id == 0u) {
        return 0u;
    }

    if (class_id == 0u) {
        start = dg_lod_lower_bound_chunk(idx, chunk_id);
        for (i = start; i < idx->count; ++i) {
            const dg_lod_index_entry *e = &idx->entries[i];
            if (e->chunk_id != chunk_id) {
                break;
            }
            out_candidates[written].key = e->key;
            out_candidates[written].pos = e->pos;
            out_candidates[written].class_id = e->class_id;
            written += 1u;
            if (written >= max_out) {
                break;
            }
        }
    } else {
        start = dg_lod_lower_bound_chunk_class(idx, chunk_id, class_id);
        for (i = start; i < idx->count; ++i) {
            const dg_lod_index_entry *e = &idx->entries[i];
            if (e->chunk_id != chunk_id) {
                break;
            }
            if (e->class_id != class_id) {
                break;
            }
            out_candidates[written].key = e->key;
            out_candidates[written].pos = e->pos;
            out_candidates[written].class_id = e->class_id;
            written += 1u;
            if (written >= max_out) {
                break;
            }
        }
    }

    return written;
}

u32 dg_lod_index_collect_chunks(const dg_lod_index *idx, dg_chunk_id *out_chunks, u32 max_out) {
    u32 written = 0u;
    u32 i;
    dg_chunk_id last = 0u;

    if (!idx || !idx->entries || !out_chunks || max_out == 0u) {
        return 0u;
    }

    for (i = 0u; i < idx->count; ++i) {
        dg_chunk_id cid = idx->entries[i].chunk_id;
        if (i == 0u || cid != last) {
            out_chunks[written++] = cid;
            last = cid;
            if (written >= max_out) {
                break;
            }
        }
    }
    return written;
}

