/*
FILE: game/rules/physical/resource_processes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements resource survey/extraction/refinement processes.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resource process outcomes are deterministic for identical inputs.
*/
#include "dominium/physical/resource_processes.h"

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

void dom_resource_process_desc_default(u32 kind,
                                       dom_resource_process_desc* out_desc)
{
    if (!out_desc) {
        return;
    }
    memset(out_desc, 0, sizeof(*out_desc));
    out_desc->kind = kind;
    out_desc->field_id = DOM_FIELD_ORE_DENSITY;
    out_desc->amount_q16 = dom_q16_from_int(1);
    out_desc->yield_q16 = dom_q16_from_int(1);
    out_desc->required_capability_mask = DOM_PHYS_CAP_EXTRACTION;
    out_desc->required_authority_mask = DOM_PHYS_AUTH_EXTRACTION;
    out_desc->cost_units = 1u;
}

static i32 dom_resource_clamp_non_negative(i32 v)
{
    return (v < 0) ? 0 : v;
}

int dom_resource_apply_process(dom_field_storage* fields,
                               const dom_resource_process_desc* desc,
                               u32 x,
                               u32 y,
                               const dom_physical_process_context* ctx,
                               dom_resource_process_result* out_result)
{
    i32 deposit = 0;
    if (out_result) {
        memset(out_result, 0, sizeof(*out_result));
        out_result->process.ok = 0;
        out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
        out_result->process.cost_units = desc ? desc->cost_units : 0u;
    }
    if (!fields || !desc) {
        if (out_result) {
            out_result->process.failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
        }
        return -1;
    }
    if (dom_physical_check_access(ctx,
                                  desc->required_capability_mask,
                                  desc->required_authority_mask,
                                  out_result ? &out_result->process : 0) != 0) {
        return -2;
    }
    (void)dom_field_get_value(fields, desc->field_id, x, y, &deposit);

    switch (desc->kind) {
        case DOM_RESOURCE_SURVEY_DEPOSIT:
            if (out_result) {
                out_result->surveyed_q16 = deposit;
            }
            if (ctx && ctx->audit) {
                dom_physical_audit_record(ctx->audit,
                                          ctx->actor_id,
                                          DOM_PHYS_EVENT_RESOURCE_SURVEY,
                                          (u64)desc->field_id,
                                          0u,
                                          (i64)deposit);
            }
            break;
        case DOM_RESOURCE_ACCESS_DEPOSIT:
            if (deposit <= 0) {
                if (out_result) {
                    out_result->process.failure_mode_id = DOM_PHYS_FAIL_RESOURCE_EMPTY;
                }
                return -3;
            }
            break;
        case DOM_RESOURCE_EXTRACT_MATERIAL:
            if (deposit <= 0) {
                if (out_result) {
                    out_result->process.failure_mode_id = DOM_PHYS_FAIL_RESOURCE_EMPTY;
                }
                return -4;
            }
            if (desc->amount_q16 > deposit) {
                if (out_result) {
                    out_result->process.failure_mode_id = DOM_PHYS_FAIL_RESOURCE_EMPTY;
                }
                return -5;
            }
            deposit = dom_resource_clamp_non_negative(deposit - desc->amount_q16);
            (void)dom_field_set_value(fields, desc->field_id, x, y, deposit);
            if (out_result) {
                out_result->extracted_q16 = desc->amount_q16;
            }
            if (ctx && ctx->audit) {
                dom_physical_audit_record(ctx->audit,
                                          ctx->actor_id,
                                          DOM_PHYS_EVENT_RESOURCE_EXTRACT,
                                          (u64)desc->field_id,
                                          0u,
                                          (i64)desc->amount_q16);
            }
            break;
        case DOM_RESOURCE_REFINE_MATERIAL:
            if (out_result) {
                i64 refined = ((i64)desc->amount_q16 * (i64)desc->yield_q16) >> 16;
                out_result->refined_q16 = (i32)refined;
                out_result->waste_q16 = desc->amount_q16 - out_result->refined_q16;
            }
            if (ctx && ctx->audit) {
                dom_physical_audit_record(ctx->audit,
                                          ctx->actor_id,
                                          DOM_PHYS_EVENT_RESOURCE_REFINE,
                                          (u64)desc->field_id,
                                          0u,
                                          (i64)desc->amount_q16);
            }
            break;
        case DOM_RESOURCE_HANDLE_TAILINGS:
            (void)dom_field_get_value(fields, DOM_FIELD_POLLUTION, x, y, &deposit);
            deposit = dom_resource_clamp_non_negative(deposit + desc->amount_q16);
            (void)dom_field_set_value(fields, DOM_FIELD_POLLUTION, x, y, deposit);
            if (out_result) {
                out_result->waste_q16 = desc->amount_q16;
            }
            if (ctx && ctx->audit) {
                dom_physical_audit_record(ctx->audit,
                                          ctx->actor_id,
                                          DOM_PHYS_EVENT_RESOURCE_TAILINGS,
                                          (u64)DOM_FIELD_POLLUTION,
                                          0u,
                                          (i64)desc->amount_q16);
            }
            break;
        case DOM_RESOURCE_TRANSPORT_OUTPUT:
            if (out_result) {
                out_result->refined_q16 = desc->amount_q16;
            }
            break;
        default:
            if (out_result) {
                out_result->process.failure_mode_id = DOM_PHYS_FAIL_CONSTRAINT;
            }
            return -6;
    }

    if (out_result) {
        out_result->process.ok = 1;
        out_result->process.failure_mode_id = DOM_PHYS_FAIL_NONE;
    }
    return 0;
}
