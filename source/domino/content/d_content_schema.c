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
        case D_FIELD_JOB_ID:
            if (d_content_schema_read_u32(&payload, &tmp.id) != 0) return -1;
            have_id = 1;
            break;
        case D_FIELD_JOB_NAME:
            tmp.name = d_content_schema_read_string(&payload, &have_name);
            if (!have_name) return -1;
            break;
        case D_FIELD_JOB_TAGS:
            if (d_content_schema_read_u32(&payload, &tmp.tags) != 0) return -1;
            break;
        case D_FIELD_JOB_PARAMS:
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
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_PACK_V1,      d_content_schema_validate_pack);
    rc |= d_content_schema_register_one(D_TLV_SCHEMA_MOD_V1,       d_content_schema_validate_mod);
    return rc;
}
