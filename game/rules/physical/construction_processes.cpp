/*
FILE: game/rules/physical/construction_processes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements construction process steps over assemblies and volume claims.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Construction process outcomes are deterministic for identical inputs.
*/
#include "dominium/physical/construction_processes.h"

#include <string.h>

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

void dom_construction_process_desc_default(u32 kind,
                                           dom_construction_process_desc* out_desc)
{
    if (!out_desc) {
        return;
    }
    memset(out_desc, 0, sizeof(*out_desc));
    out_desc->kind = kind;
    out_desc->required_capability_mask = DOM_PHYS_CAP_CONSTRUCTION;
    out_desc->required_authority_mask = DOM_PHYS_AUTH_CONSTRUCTION;
    out_desc->cost_units = 1u;
}

int dom_construction_apply(dom_assembly* assembly,
                           dom_field_storage* fields,
                           dom_volume_claim_registry* claims,
                           const dom_construction_process_desc* desc,
                           const dom_construction_request* request,
                           const dom_physical_process_context* ctx,
                           dom_physical_process_result* out_result)
{
    i32 bearing = 0;
    if (out_result) {
        memset(out_result, 0, sizeof(*out_result));
        out_result->ok = 0;
        out_result->failure_mode_id = DOM_PHYS_FAIL_NONE;
        out_result->cost_units = desc ? desc->cost_units : 0u;
    }
    if (!desc || !request) {
        return -1;
    }
    if (dom_physical_check_access(ctx,
                                  desc->required_capability_mask,
                                  desc->required_authority_mask,
                                  out_result) != 0) {
        return -2;
    }

    switch (request->kind) {
        case DOM_CONSTRUCT_SURVEY_SITE:
            if (ctx && ctx->audit) {
                dom_physical_audit_record(ctx->audit,
                                          ctx->actor_id,
                                          DOM_PHYS_EVENT_STRUCTURE_BUILD,
                                          (assembly ? assembly->assembly_id : 0u),
                                          0u,
                                          0);
            }
            break;
        case DOM_CONSTRUCT_PREPARE_GROUND:
            if (fields) {
                (void)dom_field_get_value(fields,
                                          DOM_FIELD_BEARING_CAPACITY,
                                          request->x,
                                          request->y,
                                          &bearing);
                if (bearing <= 0) {
                    if (out_result) {
                        out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
                    }
                    return -3;
                }
            }
            break;
        case DOM_CONSTRUCT_LAY_FOUNDATION:
            if (assembly) {
                (void)dom_assembly_set_grounded(assembly, request->ground_part_index, 1);
            }
            if (claims && request->claim) {
                if (dom_volume_claim_register(claims, request->claim, ctx ? ctx->audit : 0,
                                              ctx ? ctx->now_act : 0u) != 0) {
                    if (out_result) {
                        out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
                    }
                    return -4;
                }
            }
            break;
        case DOM_CONSTRUCT_PLACE_PART:
            if (assembly && request->part_desc) {
                if (dom_assembly_add_part(assembly, request->part_desc, 0) != 0) {
                    if (out_result) {
                        out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
                    }
                    return -5;
                }
            }
            break;
        case DOM_CONSTRUCT_CONNECT_INTERFACE:
            if (assembly) {
                if (dom_assembly_connect(assembly,
                                         request->part_a,
                                         request->part_b,
                                         request->interface_mask) != 0) {
                    if (out_result) {
                        out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
                    }
                    return -6;
                }
            }
            break;
        case DOM_CONSTRUCT_INSPECT:
            if (assembly && dom_assembly_check_support(assembly) == 0) {
                if (ctx && ctx->audit) {
                    dom_physical_audit_record(ctx->audit,
                                              ctx->actor_id,
                                              DOM_PHYS_EVENT_STRUCTURE_FAIL,
                                              assembly->assembly_id,
                                              0u,
                                              0);
                }
                if (out_result) {
                    out_result->failure_mode_id = DOM_PHYS_FAIL_UNSUPPORTED;
                }
                return -7;
            }
            break;
        case DOM_CONSTRUCT_CERTIFY:
            if (ctx && ctx->audit) {
                dom_physical_audit_record(ctx->audit,
                                          ctx->actor_id,
                                          DOM_PHYS_EVENT_STRUCTURE_BUILD,
                                          (assembly ? assembly->assembly_id : 0u),
                                          0u,
                                          1);
            }
            break;
        default:
            if (out_result) {
                out_result->failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
            }
            return -8;
    }

    if (out_result) {
        out_result->ok = 1;
        out_result->failure_mode_id = DOM_PHYS_FAIL_NONE;
    }
    return 0;
}
