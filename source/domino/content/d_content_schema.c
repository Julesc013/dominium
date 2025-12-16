/*
FILE: source/domino/content/d_content_schema.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / content/d_content_schema
RESPONSIBILITY: Implements `d_content_schema`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "content/d_content_schema.h"
#include "content/d_content.h"
#include "core/d_tlv_schema.h"

/* Basic TLV reader for content payloads: tag (u32) + length (u32) + bytes. */
static int d_content_schema_next(const d_tlv_blob *blob,
                                 u32 *offset,
                                 u32 *tag,
                                 d_tlv_blob *payload)
{
    u32 remaining;
    u32 len;
    if (!blob || !offset || !tag || !payload) {
        return -1;
    }
    if (*offset >= blob->len) {
        return 1; /* end-of-blob */
    }

    remaining = blob->len - *offset;
    if (remaining < 8u) {
        return -1;
    }

    memcpy(tag, blob->ptr + *offset, sizeof(u32));
    memcpy(&len, blob->ptr + *offset + 4u, sizeof(u32));
    *offset += 8u;
    if (len > blob->len - *offset) {
        return -1;
    }

    payload->ptr = blob->ptr + *offset;
    payload->len = len;
    *offset += len;
    return 0;
}

static int d_content_schema_read_u32(const d_tlv_blob *payload, u32 *out)
{
    if (!payload || !out) {
        return -1;
    }
    if (payload->len != 4u || payload->ptr == (unsigned char *)0) {
        return -1;
    }
    memcpy(out, payload->ptr, sizeof(u32));
    return 0;
}

static int d_content_schema_read_u16(const d_tlv_blob *payload, u16 *out)
{
    if (!payload || !out) {
        return -1;
    }
    if (payload->ptr == (unsigned char *)0) {
        return -1;
    }
    if (payload->len == 2u) {
        memcpy(out, payload->ptr, sizeof(u16));
        return 0;
    }
    if (payload->len == 4u) {
        u32 tmp;
        memcpy(&tmp, payload->ptr, sizeof(u32));
        *out = (u16)tmp;
        return 0;
    }
    return -1;
}

static int d_content_schema_read_q16_16(const d_tlv_blob *payload, q16_16 *out)
{
    i32 tmp;
    if (!payload || !out) {
        return -1;
    }
    if (payload->len != 4u || payload->ptr == (unsigned char *)0) {
        return -1;
    }
    memcpy(&tmp, payload->ptr, sizeof(i32));
    *out = (q16_16)tmp;
    return 0;
}

static int d_content_schema_read_q32_32(const d_tlv_blob *payload, q32_32 *out)
{
    q32_32 tmp;
    if (!payload || !out) {
        return -1;
    }
    if (payload->len != 8u || payload->ptr == (unsigned char *)0) {
        return -1;
    }
    memcpy(&tmp, payload->ptr, sizeof(q32_32));
    *out = tmp;
    return 0;
}

static const char *d_content_schema_read_string(const d_tlv_blob *payload, int *ok)
{
    if (ok) {
        *ok = 0;
    }
    if (!payload || payload->ptr == (unsigned char *)0) {
        return "";
    }
    if (payload->len == 0u) {
        if (ok) *ok = 1;
        return "";
    }
    if (payload->ptr[payload->len - 1u] != '\0') {
        return "";
    }
    if (ok) {
        *ok = 1;
    }
    return (const char *)payload->ptr;
}

static d_tlv_blob d_content_schema_copy_blob(const d_tlv_blob *payload)
{
    d_tlv_blob out;
    if (!payload || payload->len == 0u) {
        out.ptr = (unsigned char *)0;
        out.len = 0u;
        return out;
    }
    out = *payload;
    return out;
}

/* Parse helpers */
int d_content_schema_parse_material_v1(const d_tlv_blob *blob, struct d_proto_material_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_material tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_MATERIAL_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_MATERIAL_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_MATERIAL_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_MATERIAL_DENSITY:
            if (d_content_schema_read_q16_16(&payload, &tmp.density) != 0) return -1;
            break;
        case D_FIELD_MATERIAL_HARDNESS:
            if (d_content_schema_read_q16_16(&payload, &tmp.hardness) != 0) return -1;
            break;
        case D_FIELD_MATERIAL_MELTING:
            if (d_content_schema_read_q16_16(&payload, &tmp.melting_point) != 0) return -1;
            break;
        case D_FIELD_MATERIAL_PERMEABILITY:
            if (d_content_schema_read_q16_16(&payload, &tmp.permeability) != 0) return -1;
            break;
        case D_FIELD_MATERIAL_POROSITY:
            if (d_content_schema_read_q16_16(&payload, &tmp.porosity) != 0) return -1;
            break;
        case D_FIELD_MATERIAL_THERMAL:
            if (d_content_schema_read_q16_16(&payload, &tmp.thermal_conductivity) != 0) return -1;
            break;
        case D_FIELD_MATERIAL_EROSION:
            if (d_content_schema_read_q16_16(&payload, &tmp.erosion_resistance) != 0) return -1;
            break;
        default:
            /* ignore unknown field */
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_item_v1(const d_tlv_blob *blob, struct d_proto_item_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_item tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_ITEM_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_ITEM_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_ITEM_MATERIAL:
            if (d_content_schema_read_u32(&payload, &tmp.material_id) != 0) return -1;
            break;
        case D_FIELD_ITEM_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_ITEM_UNIT_MASS:
            if (d_content_schema_read_q16_16(&payload, &tmp.unit_mass) != 0) return -1;
            break;
        case D_FIELD_ITEM_UNIT_VOLUME:
            if (d_content_schema_read_q16_16(&payload, &tmp.unit_volume) != 0) return -1;
            break;
        case D_FIELD_ITEM_BASE_VALUE:
            if (d_content_schema_read_q16_16(&payload, &tmp.base_value) != 0) return -1;
            break;
        case D_FIELD_ITEM_CATEGORY:
            if (d_content_schema_read_u16(&payload, &tmp.category) != 0) return -1;
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_container_v1(const d_tlv_blob *blob, struct d_proto_container_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_container tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_CONTAINER_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_CONTAINER_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_CONTAINER_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_CONTAINER_MAX_VOLUME:
            if (d_content_schema_read_q16_16(&payload, &tmp.max_volume) != 0) return -1;
            break;
        case D_FIELD_CONTAINER_MAX_MASS:
            if (d_content_schema_read_q16_16(&payload, &tmp.max_mass) != 0) return -1;
            break;
        case D_FIELD_CONTAINER_SLOTS:
            if (d_content_schema_read_u16(&payload, &tmp.slot_count) != 0) return -1;
            break;
        case D_FIELD_CONTAINER_PACKING_MODE:
            if (d_content_schema_read_u16(&payload, &tmp.packing_mode) != 0) return -1;
            break;
        case D_FIELD_CONTAINER_PARAMS:
            tmp.params = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_process_v1(const d_tlv_blob *blob, struct d_proto_process_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_process tmp;
    int have_id = 0;
    int have_name = 0;
    u32 io_count = 0u;
    u32 ry_count = 0u;

#define D_CONTENT_SCHEMA_MAX_PROCESS_IO_TERMS 64u
    static d_process_io_term io_scratch[D_CONTENT_SCHEMA_MAX_PROCESS_IO_TERMS];
#define D_CONTENT_SCHEMA_MAX_PROCESS_RESEARCH_YIELDS 16u
    static d_research_point_yield ry_scratch[D_CONTENT_SCHEMA_MAX_PROCESS_RESEARCH_YIELDS];

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));
    tmp.base_duration = d_q16_16_from_int(1);
    tmp.io_count = 0u;
    tmp.io_terms = (d_process_io_term *)0;
    tmp.research_yield_count = 0u;
    tmp.research_yields = (d_research_point_yield *)0;

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_PROCESS_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_PROCESS_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_PROCESS_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_PROCESS_PARAMS:
            tmp.params = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_PROCESS_BASE_DURATION:
            if (d_content_schema_read_q16_16(&payload, &tmp.base_duration) != 0) return -1;
            break;
        case D_FIELD_PROCESS_IO_TERM: {
            d_process_io_term term;
            u32 inner_off = 0u;
            u32 inner_tag;
            d_tlv_blob inner_payload;
            int inner_rc;

            memset(&term, 0, sizeof(term));
            while ((inner_rc = d_content_schema_next(&payload, &inner_off, &inner_tag, &inner_payload)) == 0) {
                switch (inner_tag) {
                case D_FIELD_PROCESS_IO_KIND:
                    if (d_content_schema_read_u16(&inner_payload, &term.kind) != 0) return -1;
                    break;
                case D_FIELD_PROCESS_IO_ITEM_ID:
                    if (d_content_schema_read_u32(&inner_payload, &term.item_id) != 0) return -1;
                    break;
                case D_FIELD_PROCESS_IO_RATE:
                    if (d_content_schema_read_q16_16(&inner_payload, &term.rate) != 0) return -1;
                    break;
                case D_FIELD_PROCESS_IO_FLAGS:
                    if (d_content_schema_read_u16(&inner_payload, &term.flags) != 0) return -1;
                    break;
                default:
                    break;
                }
            }

            if (io_count < D_CONTENT_SCHEMA_MAX_PROCESS_IO_TERMS) {
                io_scratch[io_count] = term;
                io_count += 1u;
            } else {
                return -1;
            }
            break;
        }
        case D_FIELD_PROCESS_RESEARCH_YIELD: {
            d_research_point_yield y;
            u32 inner_off = 0u;
            u32 inner_tag;
            d_tlv_blob inner_payload;
            int inner_rc;

            memset(&y, 0, sizeof(y));
            while ((inner_rc = d_content_schema_next(&payload, &inner_off, &inner_tag, &inner_payload)) == 0) {
                switch (inner_tag) {
                case D_FIELD_RY_KIND:
                    if (d_content_schema_read_u16(&inner_payload, &y.kind) != 0) return -1;
                    break;
                case D_FIELD_RY_AMOUNT:
                    if (d_content_schema_read_q32_32(&inner_payload, &y.amount) != 0) return -1;
                    break;
                default:
                    break;
                }
            }

            if (ry_count < D_CONTENT_SCHEMA_MAX_PROCESS_RESEARCH_YIELDS) {
                ry_scratch[ry_count] = y;
                ry_count += 1u;
            } else {
                return -1;
            }
            break;
        }
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    tmp.io_count = (u16)io_count;
    tmp.io_terms = (io_count > 0u) ? io_scratch : (d_process_io_term *)0;
    tmp.research_yield_count = (u16)ry_count;
    tmp.research_yields = (ry_count > 0u) ? ry_scratch : (d_research_point_yield *)0;
    *out = tmp;
    return 0;
}

int d_content_schema_parse_deposit_v1(const d_tlv_blob *blob, struct d_proto_deposit_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_deposit tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_DEPOSIT_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_DEPOSIT_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_DEPOSIT_MATERIAL:
            if (d_content_schema_read_u32(&payload, &tmp.material_id) != 0) return -1;
            break;
        case D_FIELD_DEPOSIT_MODEL:
            if (d_content_schema_read_u16(&payload, &tmp.model_id) != 0) return -1;
            break;
        case D_FIELD_DEPOSIT_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_DEPOSIT_PARAMS:
            tmp.model_params = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_structure_v1(const d_tlv_blob *blob, struct d_proto_structure_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_structure tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_STRUCTURE_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_STRUCTURE_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_STRUCTURE_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_STRUCTURE_LAYOUT:
            tmp.layout = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_STRUCTURE_IO:
            tmp.io = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_STRUCTURE_PROCESSES:
            tmp.processes = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_vehicle_v1(const d_tlv_blob *blob, struct d_proto_vehicle_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_vehicle tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_VEHICLE_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_VEHICLE_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_VEHICLE_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_VEHICLE_PARAMS:
            tmp.params = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_spline_v1(const d_tlv_blob *blob, struct d_proto_spline_profile_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_spline_profile tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_SPLINE_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_SPLINE_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_SPLINE_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_SPLINE_PARAMS:
            tmp.params = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_SPLINE_TYPE:
            if (d_content_schema_read_u16(&payload, &tmp.type) != 0) return -1;
            break;
        case D_FIELD_SPLINE_FLAGS:
            if (d_content_schema_read_u16(&payload, &tmp.flags) != 0) return -1;
            break;
        case D_FIELD_SPLINE_BASE_SPEED:
            if (d_content_schema_read_q16_16(&payload, &tmp.base_speed) != 0) return -1;
            break;
        case D_FIELD_SPLINE_MAX_GRADE:
            if (d_content_schema_read_q16_16(&payload, &tmp.max_grade) != 0) return -1;
            break;
        case D_FIELD_SPLINE_CAPACITY:
            if (d_content_schema_read_q16_16(&payload, &tmp.capacity) != 0) return -1;
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_job_template_v1(const d_tlv_blob *blob, struct d_proto_job_template_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_job_template tmp;
    int have_id = 0;
    int have_name = 0;
    int have_purpose = 0;
    u32 ry_count = 0u;

#define D_CONTENT_SCHEMA_MAX_JOB_RESEARCH_YIELDS 16u
    static d_research_point_yield ry_scratch[D_CONTENT_SCHEMA_MAX_JOB_RESEARCH_YIELDS];

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));
    tmp.research_yield_count = 0u;
    tmp.research_yields = (d_research_point_yield *)0;

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_JOB_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_JOB_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_JOB_PURPOSE:
            if (d_content_schema_read_u16(&payload, &tmp.purpose) != 0) return -1;
            have_purpose = 1;
            break;
        case D_FIELD_JOB_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_JOB_PROCESS_ID:
            if (d_content_schema_read_u32(&payload, &tmp.process_id) != 0) return -1;
            break;
        case D_FIELD_JOB_STRUCTURE_ID:
            if (d_content_schema_read_u32(&payload, &tmp.structure_id) != 0) return -1;
            break;
        case D_FIELD_JOB_SPLINE_PROFILE_ID:
            if (d_content_schema_read_u32(&payload, &tmp.spline_profile_id) != 0) return -1;
            break;
        case D_FIELD_JOB_REQUIREMENTS:
            tmp.requirements = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_JOB_REWARDS:
            tmp.rewards = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_JOB_RESEARCH_YIELD: {
            d_research_point_yield y;
            u32 inner_off = 0u;
            u32 inner_tag;
            d_tlv_blob inner_payload;
            int inner_rc;

            memset(&y, 0, sizeof(y));
            while ((inner_rc = d_content_schema_next(&payload, &inner_off, &inner_tag, &inner_payload)) == 0) {
                switch (inner_tag) {
                case D_FIELD_RY_KIND:
                    if (d_content_schema_read_u16(&inner_payload, &y.kind) != 0) return -1;
                    break;
                case D_FIELD_RY_AMOUNT:
                    if (d_content_schema_read_q32_32(&inner_payload, &y.amount) != 0) return -1;
                    break;
                default:
                    break;
                }
            }

            if (ry_count < D_CONTENT_SCHEMA_MAX_JOB_RESEARCH_YIELDS) {
                ry_scratch[ry_count] = y;
                ry_count += 1u;
            } else {
                return -1;
            }
            break;
        }
        default:
            break;
        }
    }

    if (!have_id || !have_name || !have_purpose) {
        return -1;
    }
    tmp.research_yield_count = (u16)ry_count;
    tmp.research_yields = (ry_count > 0u) ? ry_scratch : (d_research_point_yield *)0;
    *out = tmp;
    return 0;
}

int d_content_schema_parse_building_v1(const d_tlv_blob *blob, struct d_proto_building_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_building tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_BUILDING_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_BUILDING_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_BUILDING_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_BUILDING_SHELL:
            tmp.shell = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_BUILDING_PARAMS:
            tmp.params = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_blueprint_v1(const d_tlv_blob *blob, struct d_proto_blueprint_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_blueprint tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_BLUEPRINT_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_BLUEPRINT_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_BLUEPRINT_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_BLUEPRINT_PAYLOAD:
            tmp.contents = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_research_v1(const d_tlv_blob *blob, struct d_proto_research_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_research tmp;
    int have_id = 0;
    int have_name = 0;
    u32 prereq_count = 0u;

#define D_CONTENT_SCHEMA_MAX_RESEARCH_PREREQS 64u
    static d_research_id prereq_scratch[D_CONTENT_SCHEMA_MAX_RESEARCH_PREREQS];

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));
    tmp.prereq_count = 0u;
    tmp.prereq_ids = (d_research_id *)0;

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_RESEARCH_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_RESEARCH_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_RESEARCH_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_RESEARCH_PREREQ_ID: {
            u32 pid = 0u;
            if (d_content_schema_read_u32(&payload, &pid) != 0) return -1;
            if (prereq_count < D_CONTENT_SCHEMA_MAX_RESEARCH_PREREQS) {
                prereq_scratch[prereq_count++] = (d_research_id)pid;
            } else {
                return -1;
            }
            break;
        }
        case D_FIELD_RESEARCH_UNLOCKS:
            tmp.unlocks = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_RESEARCH_COST:
            tmp.cost = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_RESEARCH_PARAMS:
            tmp.params = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    tmp.prereq_count = (u16)prereq_count;
    tmp.prereq_ids = (prereq_count > 0u) ? prereq_scratch : (d_research_id *)0;
    *out = tmp;
    return 0;
}

int d_content_schema_parse_research_point_source_v1(
    const d_tlv_blob *blob,
    struct d_proto_research_point_source_s *out
) {
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_research_point_source tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_RP_SOURCE_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_RP_SOURCE_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_RP_SOURCE_KIND:
            if (d_content_schema_read_u16(&payload, &tmp.kind) != 0) return -1;
            break;
        case D_FIELD_RP_SOURCE_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_RP_SOURCE_PARAMS:
            tmp.params = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_policy_rule_v1(
    const d_tlv_blob *blob,
    struct d_proto_policy_rule_s *out
) {
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_policy_rule tmp;
    int have_id = 0;
    int have_name = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_POLICY_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_POLICY_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_POLICY_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_POLICY_SCOPE:
            tmp.scope = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_POLICY_EFFECT:
            tmp.effect = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_POLICY_CONDITIONS:
            tmp.conditions = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_name) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_pack_v1(const d_tlv_blob *blob, struct d_proto_pack_manifest_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_pack_manifest tmp;
    int have_id = 0;
    int have_version = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_PACK_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_PACK_VERSION:
            if (d_content_schema_read_u32(&payload, &tmp.version) != 0) return -1;
            have_version = 1;
            break;
        case D_FIELD_PACK_NAME:
            tmp.name = d_content_schema_read_string(&payload, (int *)0);
            break;
        case D_FIELD_PACK_DESCRIPTION:
            tmp.description = d_content_schema_read_string(&payload, (int *)0);
            break;
        case D_FIELD_PACK_CONTENT:
            tmp.content_tlv = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_version) {
        return -1;
    }
    *out = tmp;
    return 0;
}

int d_content_schema_parse_mod_v1(const d_tlv_blob *blob, struct d_proto_mod_manifest_s *out)
{
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_proto_mod_manifest tmp;
    int have_id = 0;
    int have_version = 0;

    if (!blob || !out) {
        return -1;
    }
    memset(&tmp, 0, sizeof(tmp));

    while (1) {
        int rc = d_content_schema_next(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }

        switch (tag) {
        case D_FIELD_MOD_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_MOD_VERSION:
            if (d_content_schema_read_u32(&payload, &tmp.version) != 0) return -1;
            have_version = 1;
            break;
        case D_FIELD_MOD_NAME:
            tmp.name = d_content_schema_read_string(&payload, (int *)0);
            break;
        case D_FIELD_MOD_DESCRIPTION:
            tmp.description = d_content_schema_read_string(&payload, (int *)0);
            break;
        case D_FIELD_MOD_DEPS:
            tmp.deps_tlv = d_content_schema_copy_blob(&payload);
            break;
        case D_FIELD_MOD_CONTENT:
            tmp.content_tlv = d_content_schema_copy_blob(&payload);
            break;
        default:
            break;
        }
    }

    if (!have_id || !have_version) {
        return -1;
    }
    *out = tmp;
    return 0;
}

/* Validators wired into the schema registry */
static int d_content_schema_validate_material(d_tlv_schema_id schema_id,
                                              u16 version,
                                              const struct d_tlv_blob *in,
                                              struct d_tlv_blob *out_upgraded)
{
    d_proto_material tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_MATERIAL_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_material_v1(in, &tmp);
}

static int d_content_schema_validate_item(d_tlv_schema_id schema_id,
                                          u16 version,
                                          const struct d_tlv_blob *in,
                                          struct d_tlv_blob *out_upgraded)
{
    d_proto_item tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_ITEM_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_item_v1(in, &tmp);
}

static int d_content_schema_validate_container(d_tlv_schema_id schema_id,
                                               u16 version,
                                               const struct d_tlv_blob *in,
                                               struct d_tlv_blob *out_upgraded)
{
    d_proto_container tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_CONTAINER_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_container_v1(in, &tmp);
}

static int d_content_schema_validate_process(d_tlv_schema_id schema_id,
                                             u16 version,
                                             const struct d_tlv_blob *in,
                                             struct d_tlv_blob *out_upgraded)
{
    d_proto_process tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_PROCESS_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_process_v1(in, &tmp);
}

static int d_content_schema_validate_deposit(d_tlv_schema_id schema_id,
                                             u16 version,
                                             const struct d_tlv_blob *in,
                                             struct d_tlv_blob *out_upgraded)
{
    d_proto_deposit tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_DEPOSIT_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_deposit_v1(in, &tmp);
}

static int d_content_schema_validate_structure(d_tlv_schema_id schema_id,
                                               u16 version,
                                               const struct d_tlv_blob *in,
                                               struct d_tlv_blob *out_upgraded)
{
    d_proto_structure tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_STRUCTURE_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_structure_v1(in, &tmp);
}

static int d_content_schema_validate_vehicle(d_tlv_schema_id schema_id,
                                             u16 version,
                                             const struct d_tlv_blob *in,
                                             struct d_tlv_blob *out_upgraded)
{
    d_proto_vehicle tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_VEHICLE_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_vehicle_v1(in, &tmp);
}

static int d_content_schema_validate_spline(d_tlv_schema_id schema_id,
                                            u16 version,
                                            const struct d_tlv_blob *in,
                                            struct d_tlv_blob *out_upgraded)
{
    d_proto_spline_profile tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_SPLINE_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_spline_v1(in, &tmp);
}

static int d_content_schema_validate_job(d_tlv_schema_id schema_id,
                                         u16 version,
                                         const struct d_tlv_blob *in,
                                         struct d_tlv_blob *out_upgraded)
{
    d_proto_job_template tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_JOB_TEMPLATE_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_job_template_v1(in, &tmp);
}

static int d_content_schema_validate_building(d_tlv_schema_id schema_id,
                                              u16 version,
                                              const struct d_tlv_blob *in,
                                              struct d_tlv_blob *out_upgraded)
{
    d_proto_building tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_BUILDING_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_building_v1(in, &tmp);
}

static int d_content_schema_validate_blueprint(d_tlv_schema_id schema_id,
                                               u16 version,
                                               const struct d_tlv_blob *in,
                                               struct d_tlv_blob *out_upgraded)
{
    d_proto_blueprint tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_BLUEPRINT_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_blueprint_v1(in, &tmp);
}

static int d_content_schema_validate_research(d_tlv_schema_id schema_id,
                                              u16 version,
                                              const struct d_tlv_blob *in,
                                              struct d_tlv_blob *out_upgraded)
{
    d_proto_research tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_RESEARCH_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_research_v1(in, &tmp);
}

static int d_content_schema_validate_research_point_source(d_tlv_schema_id schema_id,
                                                           u16 version,
                                                           const struct d_tlv_blob *in,
                                                           struct d_tlv_blob *out_upgraded)
{
    d_proto_research_point_source tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_RESEARCH_POINT_SOURCE_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_research_point_source_v1(in, &tmp);
}

static int d_content_schema_validate_policy_rule(d_tlv_schema_id schema_id,
                                                 u16 version,
                                                 const struct d_tlv_blob *in,
                                                 struct d_tlv_blob *out_upgraded)
{
    d_proto_policy_rule tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_POLICY_RULE_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_policy_rule_v1(in, &tmp);
}

static int d_content_schema_validate_pack(d_tlv_schema_id schema_id,
                                          u16 version,
                                          const struct d_tlv_blob *in,
                                          struct d_tlv_blob *out_upgraded)
{
    d_proto_pack_manifest tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_PACK_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_pack_v1(in, &tmp);
}

static int d_content_schema_validate_mod(d_tlv_schema_id schema_id,
                                         u16 version,
                                         const struct d_tlv_blob *in,
                                         struct d_tlv_blob *out_upgraded)
{
    d_proto_mod_manifest tmp;
    (void)out_upgraded;
    if (schema_id != D_TLV_SCHEMA_MOD_V1 || version != 1u) {
        return -1;
    }
    return d_content_schema_parse_mod_v1(in, &tmp);
}

static int d_content_schema_register_one(d_tlv_schema_id id,
                                         d_tlv_schema_validate_fn fn)
{
    d_tlv_schema_desc desc;
    desc.schema_id = id;
    desc.version = 1u;
    desc.validate_fn = fn;
    return d_tlv_schema_register(&desc);
}

int d_content_schema_register_all(void)
{
    int rc = 0;
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_MATERIAL_V1,  d_content_schema_validate_material);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_ITEM_V1,      d_content_schema_validate_item);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_CONTAINER_V1, d_content_schema_validate_container);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_PROCESS_V1,   d_content_schema_validate_process);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_DEPOSIT_V1,   d_content_schema_validate_deposit);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_STRUCTURE_V1, d_content_schema_validate_structure);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_VEHICLE_V1,   d_content_schema_validate_vehicle);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_SPLINE_V1,    d_content_schema_validate_spline);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_JOB_TEMPLATE_V1, d_content_schema_validate_job);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_BUILDING_V1,  d_content_schema_validate_building);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_BLUEPRINT_V1, d_content_schema_validate_blueprint);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_RESEARCH_V1,  d_content_schema_validate_research);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_RESEARCH_POINT_SOURCE_V1, d_content_schema_validate_research_point_source);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_POLICY_RULE_V1, d_content_schema_validate_policy_rule);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_PACK_V1,      d_content_schema_validate_pack);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_MOD_V1,       d_content_schema_validate_mod);
    return rc;
}
