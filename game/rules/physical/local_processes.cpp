/*
FILE: game/rules/physical/local_processes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements local physical interaction processes (survey/collect/assemble/connect/inspect/repair).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Local process outcomes are deterministic for identical inputs.
*/
#include "dominium/physical/local_processes.h"

#include "dominium/physical/resource_processes.h"
#include "dominium/physical/construction_processes.h"

#include <string.h>

#define DOM_LOCAL_SURVEY_CONFIDENCE_Q16 49152 /* ~0.75 */
#define DOM_LOCAL_SURVEY_NOISE_Q16 4096       /* ~0.0625 */

static i32 dom_local_abs_i32(i32 v)
{
    return (v < 0) ? -v : v;
}

static u32 dom_local_hash32(u64 v)
{
    v ^= v >> 33;
    v *= 0xff51afd7ed558ccdULL;
    v ^= v >> 33;
    v *= 0xc4ceb9fe1a85ec53ULL;
    v ^= v >> 33;
    return (u32)v;
}

static i32 dom_local_noise_q16(u64 seed, u32 salt, i32 amplitude_q16)
{
    u64 mix = seed ^ ((u64)salt * 0x9e3779b97f4a7c15ULL);
    u32 h = dom_local_hash32(mix);
    u32 span;
    if (amplitude_q16 <= 0) {
        return 0;
    }
    span = (u32)(amplitude_q16 * 2 + 1);
    return (i32)(h % span) - amplitude_q16;
}

static int dom_local_check_access(const dom_local_process_context* ctx,
                                  u32 required_caps,
                                  u32 required_auth,
                                  dom_physical_process_result* out_result)
{
    if (!ctx) {
        return -1;
    }
    if ((ctx->phys.capability_mask & required_caps) != required_caps) {
        if (out_result) {
            out_result->ok = 0;
            out_result->failure_mode_id = DOM_PHYS_FAIL_NO_CAPABILITY;
        }
        return -2;
    }
    if ((ctx->phys.authority_mask & required_auth) != required_auth) {
        if (out_result) {
            out_result->ok = 0;
            out_result->failure_mode_id = DOM_PHYS_FAIL_NO_AUTHORITY;
        }
        return -3;
    }
    return 0;
}

static int dom_local_required_fields_available(dom_field_storage* storage, u32 mask)
{
    u32 i;
    if (!storage || mask == 0u) {
        return 1;
    }
    for (i = 0u; i < 32u; ++i) {
        u32 bit = (1u << i);
        if ((mask & bit) == 0u) {
            continue;
        }
        if (!dom_field_layer_find(storage, i + 1u)) {
            return 0;
        }
    }
    return 1;
}

static int dom_local_epistemic_fail(const dom_local_process_context* ctx,
                                    u32 required_field_mask,
                                    u32 kind)
{
    u32 roll;
    if (!ctx) {
        return 0;
    }
    if (kind == DOM_LOCAL_PROCESS_SURVEY) {
        return 0;
    }
    if ((ctx->knowledge_mask & required_field_mask) == required_field_mask) {
        return 0;
    }
    roll = dom_local_hash32(ctx->rng_seed ^ (u64)kind);
    roll &= 0xFFFFu;
    if (roll > (ctx->confidence_q16 & 0xFFFFu)) {
        return 1;
    }
    return 0;
}

void dom_local_process_desc_default(u32 kind,
                                    dom_local_process_desc* out_desc)
{
    if (!out_desc) {
        return;
    }
    memset(out_desc, 0, sizeof(*out_desc));
    out_desc->kind = kind;
    out_desc->cost_units = 1u;
    out_desc->resource_amount_q16 = (i32)(1 << 16);
    out_desc->energy_load_q16 = (i32)(1 << 16);
    out_desc->min_support_capacity_q16 = (i32)(1 << 16);
    out_desc->max_surface_gradient_q16 = (i32)(10 << 16);

    switch (kind) {
        case DOM_LOCAL_PROCESS_SURVEY:
            out_desc->required_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_SUPPORT_CAPACITY) |
                DOM_FIELD_BIT(DOM_FIELD_SURFACE_GRADIENT) |
                DOM_FIELD_BIT(DOM_FIELD_LOCAL_MOISTURE) |
                DOM_FIELD_BIT(DOM_FIELD_ACCESSIBILITY_COST);
            out_desc->required_capability_mask = DOM_PHYS_CAP_TERRAIN;
            out_desc->required_authority_mask = DOM_PHYS_AUTH_TERRAIN;
            break;
        case DOM_LOCAL_PROCESS_COLLECT:
            out_desc->required_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_SUPPORT_CAPACITY) |
                DOM_FIELD_BIT(DOM_FIELD_SURFACE_GRADIENT) |
                DOM_FIELD_BIT(DOM_FIELD_LOCAL_MOISTURE);
            out_desc->required_capability_mask = DOM_PHYS_CAP_EXTRACTION;
            out_desc->required_authority_mask = DOM_PHYS_AUTH_EXTRACTION;
            break;
        case DOM_LOCAL_PROCESS_ASSEMBLE:
            out_desc->required_field_mask =
                DOM_FIELD_BIT(DOM_FIELD_SUPPORT_CAPACITY) |
                DOM_FIELD_BIT(DOM_FIELD_SURFACE_GRADIENT);
            out_desc->required_capability_mask = DOM_PHYS_CAP_CONSTRUCTION;
            out_desc->required_authority_mask = DOM_PHYS_AUTH_CONSTRUCTION;
            break;
        case DOM_LOCAL_PROCESS_CONNECT_ENERGY:
            out_desc->required_capability_mask = DOM_PHYS_CAP_NETWORK;
            out_desc->required_authority_mask = DOM_PHYS_AUTH_NETWORK;
            break;
        case DOM_LOCAL_PROCESS_INSPECT:
            out_desc->required_capability_mask = DOM_PHYS_CAP_CONSTRUCTION;
            out_desc->required_authority_mask = DOM_PHYS_AUTH_CONSTRUCTION;
            break;
        case DOM_LOCAL_PROCESS_REPAIR:
            out_desc->required_capability_mask = DOM_PHYS_CAP_MACHINE;
            out_desc->required_authority_mask = DOM_PHYS_AUTH_MAINTENANCE;
            out_desc->required_field_mask = DOM_FIELD_BIT(DOM_FIELD_LOCAL_MOISTURE);
            break;
        default:
            break;
    }
}

static int dom_local_check_support(dom_field_storage* storage,
                                   u32 x,
                                   u32 y,
                                   i32 min_support_q16,
                                   i32 max_gradient_q16,
                                   dom_physical_process_result* out_result)
{
    i32 support = 0;
    i32 gradient = 0;
    if (!storage) {
        return 0;
    }
    (void)dom_field_get_value(storage, DOM_FIELD_SUPPORT_CAPACITY, x, y, &support);
    (void)dom_field_get_value(storage, DOM_FIELD_SURFACE_GRADIENT, x, y, &gradient);
    if (min_support_q16 > 0 && support < min_support_q16) {
        if (out_result) {
            out_result->ok = 0;
            out_result->failure_mode_id = DOM_PHYS_FAIL_CAPACITY;
        }
        return -1;
    }
    if (max_gradient_q16 > 0 && gradient > max_gradient_q16) {
        if (out_result) {
            out_result->ok = 0;
            out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
        }
        return -2;
    }
    return 0;
}

static void dom_local_apply_failure_effect(dom_field_storage* storage,
                                           u32 x,
                                           u32 y,
                                           i32 delta_q16)
{
    i32 value = 0;
    if (!storage) {
        return;
    }
    if (dom_field_get_value(storage, DOM_FIELD_ACCESSIBILITY_COST, x, y, &value) != 0) {
        return;
    }
    value += delta_q16;
    (void)dom_field_set_value(storage, DOM_FIELD_ACCESSIBILITY_COST, x, y, value);
}

int dom_local_process_apply(dom_local_process_world* world,
                            const dom_local_process_desc* desc,
                            u32 x,
                            u32 y,
                            const dom_local_process_context* ctx,
                            dom_local_process_result* out_result)
{
    dom_physical_process_result* phys_result = 0;
    if (out_result) {
        memset(out_result, 0, sizeof(*out_result));
        out_result->process.ok = 0;
        out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
        out_result->process.cost_units = desc ? desc->cost_units : 0u;
        out_result->confidence_q16 = 0u;
        out_result->uncertainty_q16 = 0u;
        out_result->surveyed_field_mask = 0u;
        phys_result = &out_result->process;
    }
    if (!world || !desc) {
        if (phys_result) {
            phys_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
        }
        return -1;
    }
    if (dom_local_check_access(ctx,
                               desc->required_capability_mask,
                               desc->required_authority_mask,
                               phys_result) != 0) {
        return -2;
    }
    if (!dom_local_required_fields_available(world->objective_fields, desc->required_field_mask)) {
        if (phys_result) {
            phys_result->failure_mode_id = DOM_PHYS_FAIL_UNSUPPORTED;
        }
        return -3;
    }
    if (dom_local_epistemic_fail(ctx, desc->required_field_mask, desc->kind)) {
        if (phys_result) {
            phys_result->failure_mode_id = DOM_PHYS_FAIL_EPISTEMIC;
        }
        return -4;
    }

    switch (desc->kind) {
        case DOM_LOCAL_PROCESS_SURVEY: {
            u32 i;
            if (!world->objective_fields || !world->subjective_fields) {
                if (phys_result) {
                    phys_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
                }
                return -5;
            }
            for (i = 0u; i < 32u; ++i) {
                u32 bit = (1u << i);
                i32 value = 0;
                i32 noise;
                if ((desc->required_field_mask & bit) == 0u) {
                    continue;
                }
                if (dom_field_get_value(world->objective_fields, i + 1u, x, y, &value) != 0) {
                    continue;
                }
                if (value == DOM_FIELD_VALUE_UNKNOWN) {
                    continue;
                }
                noise = dom_local_noise_q16(ctx ? ctx->rng_seed : 0u, i + 1u, DOM_LOCAL_SURVEY_NOISE_Q16);
                (void)dom_field_set_value(world->subjective_fields, i + 1u, x, y, value + noise);
                if (out_result) {
                    out_result->uncertainty_q16 += (u32)dom_local_abs_i32(noise);
                }
            }
            if (out_result) {
                out_result->surveyed_field_mask = desc->required_field_mask;
                out_result->confidence_q16 = DOM_LOCAL_SURVEY_CONFIDENCE_Q16;
                out_result->process.ok = 1;
                out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
            }
            return 0;
        }
        case DOM_LOCAL_PROCESS_COLLECT: {
            i32 material = 0;
            if (dom_local_check_support(world->objective_fields,
                                        x, y,
                                        desc->min_support_capacity_q16,
                                        desc->max_surface_gradient_q16,
                                        phys_result) != 0) {
                dom_local_apply_failure_effect(world->objective_fields, x, y, (i32)(1 << 15));
                return -6;
            }
            (void)dom_field_get_value(world->objective_fields,
                                      DOM_FIELD_LOCAL_MOISTURE, x, y, &material);
            if (material <= 0 || material < desc->resource_amount_q16) {
                if (phys_result) {
                    phys_result->failure_mode_id = DOM_PHYS_FAIL_RESOURCE_EMPTY;
                }
                dom_local_apply_failure_effect(world->objective_fields, x, y, (i32)(1 << 14));
                return -7;
            }
            material -= desc->resource_amount_q16;
            (void)dom_field_set_value(world->objective_fields,
                                      DOM_FIELD_LOCAL_MOISTURE, x, y, material);
            out_result->process.ok = 1;
            out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
            return 0;
        }
        case DOM_LOCAL_PROCESS_ASSEMBLE: {
            dom_construction_process_desc cdesc;
            dom_construction_request req;
            dom_physical_part_desc part_desc;
            u32 part_index = 0u;
            if (!world->assembly) {
                if (phys_result) {
                    phys_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
                }
                return -8;
            }
            if (dom_local_check_support(world->objective_fields,
                                        x, y,
                                        desc->min_support_capacity_q16,
                                        desc->max_surface_gradient_q16,
                                        phys_result) != 0) {
                dom_local_apply_failure_effect(world->objective_fields, x, y, (i32)(1 << 15));
                return -9;
            }
            memset(&part_desc, 0, sizeof(part_desc));
            part_desc.part_id = 1u;
            part_desc.mass_kg_q16 = (MassKg)(1 << 16);
            part_desc.volume_m3_q16 = (VolM3)(1 << 16);
            part_desc.interface_mask = DOM_PART_IFACE_MECHANICAL;
            part_desc.flags = DOM_PART_FLAG_REQUIRES_SUPPORT;

            dom_construction_process_desc_default(DOM_CONSTRUCT_PLACE_PART, &cdesc);
            memset(&req, 0, sizeof(req));
            req.kind = DOM_CONSTRUCT_PLACE_PART;
            req.part_desc = &part_desc;
            if (dom_construction_apply(world->assembly,
                                       world->objective_fields,
                                       world->claims,
                                       &cdesc, &req,
                                       ctx ? &ctx->phys : 0,
                                       phys_result) != 0) {
                return -10;
            }
            part_index = world->assembly->part_count ? (world->assembly->part_count - 1u) : 0u;
            dom_construction_process_desc_default(DOM_CONSTRUCT_LAY_FOUNDATION, &cdesc);
            memset(&req, 0, sizeof(req));
            req.kind = DOM_CONSTRUCT_LAY_FOUNDATION;
            req.ground_part_index = part_index;
            if (dom_construction_apply(world->assembly,
                                       world->objective_fields,
                                       world->claims,
                                       &cdesc, &req,
                                       ctx ? &ctx->phys : 0,
                                       phys_result) != 0) {
                return -11;
            }
            dom_construction_process_desc_default(DOM_CONSTRUCT_INSPECT, &cdesc);
            memset(&req, 0, sizeof(req));
            req.kind = DOM_CONSTRUCT_INSPECT;
            if (dom_construction_apply(world->assembly,
                                       world->objective_fields,
                                       world->claims,
                                       &cdesc, &req,
                                       ctx ? &ctx->phys : 0,
                                       phys_result) != 0) {
                if (world->structure) {
                    world->structure->failed = 1u;
                }
                return -12;
            }
            if (world->structure) {
                world->structure->built = 1u;
                world->structure->failed = 0u;
            }
            out_result->process.ok = 1;
            out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
            return 0;
        }
        case DOM_LOCAL_PROCESS_CONNECT_ENERGY: {
            int rc;
            if (!world->network) {
                if (phys_result) {
                    phys_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
                }
                return -13;
            }
            rc = dom_network_route_flow(world->network,
                                        1u, 2u,
                                        desc->energy_load_q16,
                                        ctx ? ctx->phys.audit : 0,
                                        ctx ? ctx->phys.now_act : 0);
            if (rc != 0) {
                if (phys_result) {
                    phys_result->failure_mode_id = (rc == -4) ? DOM_PHYS_FAIL_CAPACITY
                                                              : DOM_PHYS_FAIL_CONSTRAINT;
                }
                return -14;
            }
            out_result->process.ok = 1;
            out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
            return 0;
        }
        case DOM_LOCAL_PROCESS_INSPECT: {
            dom_construction_process_desc cdesc;
            dom_construction_request req;
            if (!world->assembly) {
                if (phys_result) {
                    phys_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
                }
                return -15;
            }
            dom_construction_process_desc_default(DOM_CONSTRUCT_INSPECT, &cdesc);
            memset(&req, 0, sizeof(req));
            req.kind = DOM_CONSTRUCT_INSPECT;
            if (dom_construction_apply(world->assembly,
                                       world->objective_fields,
                                       world->claims,
                                       &cdesc, &req,
                                       ctx ? &ctx->phys : 0,
                                       phys_result) != 0) {
                if (world->structure) {
                    world->structure->failed = 1u;
                }
                return -16;
            }
            if (world->structure) {
                world->structure->failed = 0u;
            }
            out_result->process.ok = 1;
            out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
            return 0;
        }
        case DOM_LOCAL_PROCESS_REPAIR: {
            i32 material = 0;
            if (!world->structure || !world->structure->built) {
                if (phys_result) {
                    phys_result->failure_mode_id = DOM_PHYS_FAIL_UNSUPPORTED;
                }
                return -17;
            }
            (void)dom_field_get_value(world->objective_fields,
                                      DOM_FIELD_LOCAL_MOISTURE, x, y, &material);
            if (material < desc->resource_amount_q16) {
                if (phys_result) {
                    phys_result->failure_mode_id = DOM_PHYS_FAIL_RESOURCE_EMPTY;
                }
                return -18;
            }
            material -= desc->resource_amount_q16;
            (void)dom_field_set_value(world->objective_fields,
                                      DOM_FIELD_LOCAL_MOISTURE, x, y, material);
            world->structure->failed = 0u;
            if (world->network) {
                (void)dom_network_repair_edge(world->network, 1u);
            }
            out_result->process.ok = 1;
            out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
            return 0;
        }
        default:
            if (phys_result) {
                phys_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
            }
            return -19;
    }
}
