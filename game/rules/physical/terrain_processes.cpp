/*
FILE: game/rules/physical/terrain_processes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements deterministic terrain modification processes.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Terrain process outcomes are deterministic for identical inputs.
*/
#include "dominium/physical/terrain_processes.h"

#include <string.h>

static i32 dom_q16_from_int(i32 v)
{
    return (i32)(v << 16);
}

static int dom_physical_check_access(const dom_physical_process_context* ctx,
                                     u32 required_caps,
                                     u32 required_auth,
                                     dom_physical_process_result* out_result)
{
    if (!ctx) {
        return -1;
    }
    if ((ctx->capability_mask & required_caps) != required_caps) {
        if (out_result) {
            out_result->ok = 0;
            out_result->failure_mode_id = DOM_PHYS_FAIL_NO_CAPABILITY;
        }
        return -2;
    }
    if ((ctx->authority_mask & required_auth) != required_auth) {
        if (out_result) {
            out_result->ok = 0;
            out_result->failure_mode_id = DOM_PHYS_FAIL_NO_AUTHORITY;
        }
        return -3;
    }
    return 0;
}

static i32 dom_physical_clamp_non_negative(i32 v)
{
    return (v < 0) ? 0 : v;
}

void dom_terrain_process_desc_default(u32 kind,
                                      dom_terrain_process_desc* out_desc)
{
    if (!out_desc) {
        return;
    }
    memset(out_desc, 0, sizeof(*out_desc));
    out_desc->kind = kind;
    out_desc->delta_q16 = dom_q16_from_int(1);
    out_desc->max_slope_q16 = dom_q16_from_int(10);
    out_desc->min_bearing_q16 = dom_q16_from_int(1);
    out_desc->required_capability_mask = DOM_PHYS_CAP_TERRAIN;
    out_desc->required_authority_mask = DOM_PHYS_AUTH_TERRAIN;
    out_desc->cost_units = 1u;

    switch (kind) {
        case DOM_TERRAIN_CLEAR_LAND:
        case DOM_TERRAIN_DEFOREST:
            out_desc->affected_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_VEGETATION_BIOMASS) |
                DOM_FIELD_BIT(DOM_FIELD_POLLUTION);
            break;
        case DOM_TERRAIN_EXCAVATE:
        case DOM_TERRAIN_FILL:
            out_desc->affected_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_ELEVATION) |
                DOM_FIELD_BIT(DOM_FIELD_POLLUTION);
            break;
        case DOM_TERRAIN_COMPACT:
            out_desc->affected_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_BEARING_CAPACITY);
            break;
        case DOM_TERRAIN_GRADE:
        case DOM_TERRAIN_TERRACE:
            out_desc->affected_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_SLOPE) |
                DOM_FIELD_BIT(DOM_FIELD_ELEVATION);
            break;
        case DOM_TERRAIN_IRRIGATE:
        case DOM_TERRAIN_DRAIN:
            out_desc->affected_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_MOISTURE) |
                DOM_FIELD_BIT(DOM_FIELD_SURFACE_WATER);
            break;
        case DOM_TERRAIN_CONTAMINATE:
        case DOM_TERRAIN_REMEDIATE:
            out_desc->affected_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_POLLUTION);
            break;
        default:
            out_desc->affected_field_mask = 0u;
            break;
    }
}

static int dom_terrain_check_constraints(dom_field_storage* fields,
                                        const dom_terrain_process_desc* desc,
                                        u32 x,
                                        u32 y,
                                        dom_physical_process_result* out_result)
{
    i32 slope = 0;
    i32 bearing = 0;
    if (!desc || !fields) {
        return 0;
    }
    (void)dom_field_get_value(fields, DOM_FIELD_SLOPE, x, y, &slope);
    (void)dom_field_get_value(fields, DOM_FIELD_BEARING_CAPACITY, x, y, &bearing);
    if (desc->max_slope_q16 > 0 && slope > desc->max_slope_q16) {
        if (out_result) {
            out_result->ok = 0;
            out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
        }
        return -1;
    }
    if (desc->min_bearing_q16 > 0 && bearing < desc->min_bearing_q16) {
        if (out_result) {
            out_result->ok = 0;
            out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
        }
        return -2;
    }
    return 0;
}

int dom_terrain_apply_process(dom_field_storage* fields,
                              const dom_terrain_process_desc* desc,
                              u32 x,
                              u32 y,
                              const dom_physical_process_context* ctx,
                              dom_physical_process_result* out_result)
{
    i32 value = 0;
    i32 delta;
    if (out_result) {
        memset(out_result, 0, sizeof(*out_result));
        out_result->ok = 0;
        out_result->failure_mode_id = DOM_PHYS_FAIL_NONE;
        out_result->cost_units = desc ? desc->cost_units : 0u;
    }
    if (!fields || !desc) {
        if (out_result) {
            out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
        }
        return -1;
    }
    if (dom_physical_check_access(ctx,
                                  desc->required_capability_mask,
                                  desc->required_authority_mask,
                                  out_result) != 0) {
        return -2;
    }
    if (dom_terrain_check_constraints(fields, desc, x, y, out_result) != 0) {
        return -3;
    }

    delta = desc->delta_q16;
    switch (desc->kind) {
        case DOM_TERRAIN_CLEAR_LAND:
        case DOM_TERRAIN_DEFOREST:
            (void)dom_field_set_value(fields, DOM_FIELD_VEGETATION_BIOMASS, x, y, 0);
            (void)dom_field_get_value(fields, DOM_FIELD_POLLUTION, x, y, &value);
            value = dom_physical_clamp_non_negative(value + (delta / 4));
            (void)dom_field_set_value(fields, DOM_FIELD_POLLUTION, x, y, value);
            break;
        case DOM_TERRAIN_EXCAVATE:
            (void)dom_field_get_value(fields, DOM_FIELD_ELEVATION, x, y, &value);
            value -= (delta < 0) ? -delta : delta;
            (void)dom_field_set_value(fields, DOM_FIELD_ELEVATION, x, y, value);
            (void)dom_field_get_value(fields, DOM_FIELD_POLLUTION, x, y, &value);
            value = dom_physical_clamp_non_negative(value + (delta / 8));
            (void)dom_field_set_value(fields, DOM_FIELD_POLLUTION, x, y, value);
            break;
        case DOM_TERRAIN_FILL:
            (void)dom_field_get_value(fields, DOM_FIELD_ELEVATION, x, y, &value);
            value += (delta < 0) ? -delta : delta;
            (void)dom_field_set_value(fields, DOM_FIELD_ELEVATION, x, y, value);
            break;
        case DOM_TERRAIN_COMPACT:
            (void)dom_field_get_value(fields, DOM_FIELD_BEARING_CAPACITY, x, y, &value);
            value += (delta < 0) ? -delta : delta;
            (void)dom_field_set_value(fields, DOM_FIELD_BEARING_CAPACITY, x, y, value);
            break;
        case DOM_TERRAIN_GRADE:
            (void)dom_field_set_value(fields, DOM_FIELD_SLOPE, x, y, 0);
            break;
        case DOM_TERRAIN_TERRACE:
            (void)dom_field_get_value(fields, DOM_FIELD_SLOPE, x, y, &value);
            value /= 2;
            (void)dom_field_set_value(fields, DOM_FIELD_SLOPE, x, y, value);
            break;
        case DOM_TERRAIN_IRRIGATE:
            (void)dom_field_get_value(fields, DOM_FIELD_MOISTURE, x, y, &value);
            value = dom_physical_clamp_non_negative(value + delta);
            (void)dom_field_set_value(fields, DOM_FIELD_MOISTURE, x, y, value);
            (void)dom_field_get_value(fields, DOM_FIELD_SURFACE_WATER, x, y, &value);
            value = dom_physical_clamp_non_negative(value + delta);
            (void)dom_field_set_value(fields, DOM_FIELD_SURFACE_WATER, x, y, value);
            break;
        case DOM_TERRAIN_DRAIN:
            (void)dom_field_get_value(fields, DOM_FIELD_MOISTURE, x, y, &value);
            value = dom_physical_clamp_non_negative(value - delta);
            (void)dom_field_set_value(fields, DOM_FIELD_MOISTURE, x, y, value);
            (void)dom_field_get_value(fields, DOM_FIELD_SURFACE_WATER, x, y, &value);
            value = dom_physical_clamp_non_negative(value - delta);
            (void)dom_field_set_value(fields, DOM_FIELD_SURFACE_WATER, x, y, value);
            break;
        case DOM_TERRAIN_CONTAMINATE:
            (void)dom_field_get_value(fields, DOM_FIELD_POLLUTION, x, y, &value);
            value = dom_physical_clamp_non_negative(value + delta);
            (void)dom_field_set_value(fields, DOM_FIELD_POLLUTION, x, y, value);
            break;
        case DOM_TERRAIN_REMEDIATE:
            (void)dom_field_get_value(fields, DOM_FIELD_POLLUTION, x, y, &value);
            value = dom_physical_clamp_non_negative(value - delta);
            (void)dom_field_set_value(fields, DOM_FIELD_POLLUTION, x, y, value);
            break;
        default:
            if (out_result) {
                out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
            }
            return -4;
    }

    if (ctx && ctx->audit) {
        dom_physical_audit_record(ctx->audit,
                                  ctx->actor_id,
                                  DOM_PHYS_EVENT_TERRAIN_MODIFY,
                                  (u64)desc->kind,
                                  0u,
                                  (i64)desc->delta_q16);
    }
    if (out_result) {
        out_result->ok = 1;
        out_result->failure_mode_id = DOM_PHYS_FAIL_NONE;
    }
    return 0;
}
