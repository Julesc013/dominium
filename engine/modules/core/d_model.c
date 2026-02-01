/*
FILE: source/domino/core/d_model.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_model
RESPONSIBILITY: Implements `d_model`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "d_model.h"

#define D_MODEL_MAX_FAMILIES        16u
#define D_MODEL_MAX_PER_FAMILY     256u

typedef struct d_model_family_bucket {
    d_model_family_id family_id;
    u32               count;
    d_model_desc      entries[D_MODEL_MAX_PER_FAMILY];
} d_model_family_bucket;

static d_model_family_bucket g_model_families[D_MODEL_MAX_FAMILIES];
static u32 g_model_family_count = 0u;

static d_model_family_bucket *d_model_find_family(d_model_family_id family_id) {
    u32 i;
    for (i = 0u; i < g_model_family_count; ++i) {
        if (g_model_families[i].family_id == family_id) {
            return &g_model_families[i];
        }
    }
    return (d_model_family_bucket *)0;
}

static d_model_family_bucket *d_model_ensure_family(d_model_family_id family_id) {
    d_model_family_bucket *bucket = d_model_find_family(family_id);
    if (bucket) {
        return bucket;
    }
    if (g_model_family_count >= D_MODEL_MAX_FAMILIES) {
        fprintf(stderr, "d_model_register: family table full\n");
        return (d_model_family_bucket *)0;
    }
    bucket = &g_model_families[g_model_family_count];
    bucket->family_id = family_id;
    bucket->count = 0u;
    g_model_family_count += 1u;
    return bucket;
}

int d_model_register(const d_model_desc *desc) {
    d_model_family_bucket *bucket;
    u32 i;
    if (!desc) {
        fprintf(stderr, "d_model_register: NULL descriptor\n");
        return -1;
    }
    if (desc->family_id == 0u || desc->model_id == 0u) {
        fprintf(stderr, "d_model_register: invalid ids\n");
        return -2;
    }

    bucket = d_model_ensure_family(desc->family_id);
    if (!bucket) {
        return -3;
    }

    for (i = 0u; i < bucket->count; ++i) {
        if (bucket->entries[i].model_id == desc->model_id) {
            fprintf(stderr, "d_model_register: duplicate model %u in family %u\n",
                    (unsigned int)desc->model_id,
                    (unsigned int)desc->family_id);
            return -4;
        }
    }
    if (bucket->count >= D_MODEL_MAX_PER_FAMILY) {
        fprintf(stderr, "d_model_register: family %u full\n", (unsigned int)desc->family_id);
        return -5;
    }

    bucket->entries[bucket->count] = *desc;
    bucket->count += 1u;
    return 0;
}

u32 d_model_count(d_model_family_id family_id) {
    d_model_family_bucket *bucket = d_model_find_family(family_id);
    if (!bucket) {
        return 0u;
    }
    return bucket->count;
}

const d_model_desc *d_model_get_by_index(d_model_family_id family_id, u32 index) {
    d_model_family_bucket *bucket = d_model_find_family(family_id);
    if (!bucket) {
        return (const d_model_desc *)0;
    }
    if (index >= bucket->count) {
        return (const d_model_desc *)0;
    }
    return &bucket->entries[index];
}

const d_model_desc *d_model_get(d_model_family_id family_id, d_model_id model_id) {
    d_model_family_bucket *bucket;
    u32 i;
    bucket = d_model_find_family(family_id);
    if (!bucket) {
        return (const d_model_desc *)0;
    }
    for (i = 0u; i < bucket->count; ++i) {
        if (bucket->entries[i].model_id == model_id) {
            return &bucket->entries[i];
        }
    }
    return (const d_model_desc *)0;
}
