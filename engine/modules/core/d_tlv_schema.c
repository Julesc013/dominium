/*
FILE: source/domino/core/d_tlv_schema.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_tlv_schema
RESPONSIBILITY: Implements `d_tlv_schema`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-supporting (schema version gates for deterministic IO); see `docs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: Schema id+version registry for TLV validation/migration; see `docs/DATA_FORMATS.md` (TLV schema registry).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "d_tlv_schema.h"

#define D_TLV_SCHEMA_MAX 256u

static d_tlv_schema_desc g_tlv_schemas[D_TLV_SCHEMA_MAX];
static u32 g_tlv_schema_count = 0u;

/* Process-global registry intended to be populated during init (not thread-safe). */
static const d_tlv_schema_desc *d_tlv_schema_find(d_tlv_schema_id schema_id, u16 version) {
    u32 i;
    for (i = 0u; i < g_tlv_schema_count; ++i) {
        if (g_tlv_schemas[i].schema_id == schema_id &&
            g_tlv_schemas[i].version == version) {
            return &g_tlv_schemas[i];
        }
    }
    return (const d_tlv_schema_desc *)0;
}

int d_tlv_schema_register(const d_tlv_schema_desc *desc) {
    if (!desc || !desc->validate_fn) {
        fprintf(stderr, "d_tlv_schema_register: invalid descriptor\n");
        return -1;
    }
    if (d_tlv_schema_find(desc->schema_id, desc->version)) {
        fprintf(stderr, "d_tlv_schema_register: duplicate schema %u v%u\n",
                (unsigned int)desc->schema_id,
                (unsigned int)desc->version);
        return -2;
    }
    if (g_tlv_schema_count >= D_TLV_SCHEMA_MAX) {
        fprintf(stderr, "d_tlv_schema_register: registry full\n");
        return -3;
    }
    g_tlv_schemas[g_tlv_schema_count] = *desc;
    g_tlv_schema_count += 1u;
    return 0;
}

int d_tlv_schema_validate(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded
) {
    const d_tlv_schema_desc *schema = d_tlv_schema_find(schema_id, version);
    if (!schema) {
        fprintf(stderr, "d_tlv_schema_validate: schema %u v%u not found\n",
                (unsigned int)schema_id,
                (unsigned int)version);
        return -1;
    }
    return schema->validate_fn(schema_id, version, in, out_upgraded);
}
