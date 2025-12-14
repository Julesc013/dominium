#include <stdlib.h>
#include <string.h>

#include "res/dg_tlv_canon.h"
#include "res/dg_tlv_validate.h"

int dg_tlv_validate_well_formed(const unsigned char *tlv, u32 tlv_len) {
    u32 offset = 0u;
    u32 tag;
    const unsigned char *payload;
    u32 payload_len;
    int rc;

    if (!tlv && tlv_len != 0u) {
        return -1;
    }

    for (;;) {
        rc = dg_tlv_next(tlv, tlv_len, &offset, &tag, &payload, &payload_len);
        if (rc != 0) {
            return (rc == 1) ? 0 : rc;
        }
    }
}

static int dg_tlv_schema_find_field_index(const dg_tlv_schema_desc *schema, u32 tag, u32 *out_index) {
    u32 i;
    if (!schema || !schema->fields || !out_index) {
        return -1;
    }
    for (i = 0u; i < schema->field_count; ++i) {
        if (schema->fields[i].tag == tag) {
            *out_index = i;
            return 0;
        }
    }
    return 1;
}

int dg_tlv_validate_against_schema(
    const dg_tlv_schema_desc *schema,
    const unsigned char      *tlv,
    u32                       tlv_len
) {
    u32 offset = 0u;
    u32 tag;
    const unsigned char *payload;
    u32 payload_len;
    u32 *counts;
    u32 i;
    int rc;

    if (!schema) {
        return dg_tlv_validate_well_formed(tlv, tlv_len);
    }

    if (!schema->fields && schema->field_count != 0u) {
        return -2;
    }

    counts = (u32 *)0;
    if (schema->field_count != 0u) {
        counts = (u32 *)malloc(sizeof(u32) * schema->field_count);
        if (!counts) {
            return -3;
        }
        for (i = 0u; i < schema->field_count; ++i) {
            counts[i] = 0u;
        }
    }

    for (;;) {
        u32 idx;

        rc = dg_tlv_next(tlv, tlv_len, &offset, &tag, &payload, &payload_len);
        if (rc != 0) {
            break;
        }

        rc = dg_tlv_schema_find_field_index(schema, tag, &idx);
        if (rc != 0) {
            if (counts) {
                free(counts);
            }
            return -4; /* unknown tag for this schema */
        }

        counts[idx] += 1u;
        if ((schema->fields[idx].flags & DG_TLV_FIELD_REPEATABLE) == 0u && counts[idx] > 1u) {
            if (counts) {
                free(counts);
            }
            return -5; /* duplicate non-repeatable tag */
        }
    }

    if (rc != 1) {
        if (counts) {
            free(counts);
        }
        return rc; /* malformed TLV */
    }

    for (i = 0u; i < schema->field_count; ++i) {
        if ((schema->fields[i].flags & DG_TLV_FIELD_REQUIRED) != 0u && counts[i] == 0u) {
            free(counts);
            return -6; /* missing required field */
        }
    }

    if (counts) {
        free(counts);
    }
    return 0;
}

