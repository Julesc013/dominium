/*
FILE: game/rules/war/interdiction.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic interdiction operations.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Interdiction scheduling is deterministic.
*/
#include "dominium/rules/war/interdiction.h"

#include <string.h>

const char* interdiction_refusal_to_string(interdiction_refusal_code code)
{
    switch (code) {
        case INTERDICTION_REFUSAL_NONE: return "none";
        case INTERDICTION_REFUSAL_INSUFFICIENT_FORCES: return "insufficient_forces";
        case INTERDICTION_REFUSAL_ROUTE_NOT_FOUND: return "route_not_found";
        case INTERDICTION_REFUSAL_OUT_OF_AUTHORITY: return "out_of_authority";
        default: return "unknown";
    }
}

void interdiction_registry_init(interdiction_registry* reg,
                                interdiction_operation* storage,
                                u32 capacity,
                                u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->operations = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(interdiction_operation) * (size_t)capacity);
    }
}

static u32 interdiction_find_index(const interdiction_registry* reg,
                                   u64 interdiction_id,
                                   int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->operations) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->operations[i].interdiction_id == interdiction_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->operations[i].interdiction_id > interdiction_id) {
            break;
        }
    }
    return i;
}

interdiction_operation* interdiction_find(interdiction_registry* reg,
                                          u64 interdiction_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->operations) {
        return 0;
    }
    idx = interdiction_find_index(reg, interdiction_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->operations[idx];
}

int interdiction_register(interdiction_registry* reg,
                          const interdiction_operation* input,
                          u64* out_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    u64 interdiction_id;
    interdiction_operation* entry;
    if (!reg || !reg->operations || !input) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    interdiction_id = input->interdiction_id;
    if (interdiction_id == 0u) {
        interdiction_id = reg->next_id++;
        if (interdiction_id == 0u) {
            interdiction_id = reg->next_id++;
        }
    }
    idx = interdiction_find_index(reg, interdiction_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->operations[i] = reg->operations[i - 1u];
    }
    entry = &reg->operations[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *input;
    entry->interdiction_id = interdiction_id;
    if (entry->status == 0u) {
        entry->status = INTERDICTION_STATUS_SCHEDULED;
    }
    if (entry->next_due_tick == 0u) {
        entry->next_due_tick = entry->schedule_act;
    }
    if (entry->provenance_ref == 0u) {
        entry->provenance_ref = interdiction_id;
    }
    reg->count += 1u;
    if (out_id) {
        *out_id = interdiction_id;
    }
    return 0;
}

int interdiction_apply(interdiction_operation* op,
                       interdiction_context* ctx,
                       interdiction_refusal_code* out_refusal)
{
    engagement input;
    u64 engagement_id = 0u;
    dom_act_time_t resolution_act;
    if (out_refusal) {
        *out_refusal = INTERDICTION_REFUSAL_NONE;
    }
    if (!op || !ctx) {
        return -1;
    }
    if (op->status != INTERDICTION_STATUS_SCHEDULED) {
        return 0;
    }
    if (ctx->routes && op->route_id != 0u &&
        !route_control_find(ctx->routes, op->route_id)) {
        if (out_refusal) {
            *out_refusal = INTERDICTION_REFUSAL_ROUTE_NOT_FOUND;
        }
        op->status = INTERDICTION_STATUS_FAILED;
        op->next_due_tick = DOM_TIME_ACT_MAX;
        return -2;
    }
    if (ctx->forces && op->attacker_force_ref != 0u &&
        !security_force_find(ctx->forces, op->attacker_force_ref)) {
        if (out_refusal) {
            *out_refusal = INTERDICTION_REFUSAL_INSUFFICIENT_FORCES;
        }
        op->status = INTERDICTION_STATUS_FAILED;
        op->next_due_tick = DOM_TIME_ACT_MAX;
        return -3;
    }
    if (ctx->forces && op->defender_force_ref != 0u &&
        !security_force_find(ctx->forces, op->defender_force_ref)) {
        if (out_refusal) {
            *out_refusal = INTERDICTION_REFUSAL_INSUFFICIENT_FORCES;
        }
        op->status = INTERDICTION_STATUS_FAILED;
        op->next_due_tick = DOM_TIME_ACT_MAX;
        return -4;
    }
    if (op->require_authority && op->authority_ref == 0u) {
        if (out_refusal) {
            *out_refusal = INTERDICTION_REFUSAL_OUT_OF_AUTHORITY;
        }
        op->status = INTERDICTION_STATUS_FAILED;
        op->next_due_tick = DOM_TIME_ACT_MAX;
        return -5;
    }
    if (op->attacker_force_ref == 0u || op->defender_force_ref == 0u) {
        if (out_refusal) {
            *out_refusal = INTERDICTION_REFUSAL_INSUFFICIENT_FORCES;
        }
        op->status = INTERDICTION_STATUS_FAILED;
        op->next_due_tick = DOM_TIME_ACT_MAX;
        return -6;
    }
    if (!ctx->engagements) {
        return -7;
    }
    memset(&input, 0, sizeof(input));
    input.engagement_id = 0u;
    input.domain_scope = op->domain_scope;
    input.participant_count = 2u;
    input.participants[0].force_id = op->attacker_force_ref;
    input.participants[0].role = ENGAGEMENT_ROLE_ATTACKER;
    input.participants[1].force_id = op->defender_force_ref;
    input.participants[1].role = ENGAGEMENT_ROLE_DEFENDER;
    input.start_act = op->schedule_act;
    resolution_act = op->schedule_act + op->resolution_delay;
    if (resolution_act < op->schedule_act) {
        resolution_act = op->schedule_act;
    }
    input.resolution_act = resolution_act;
    input.objective = ENGAGEMENT_OBJECTIVE_RAID;
    input.provenance_ref = op->provenance_ref;
    if (engagement_register(ctx->engagements, &input, &engagement_id) != 0) {
        return -8;
    }
    if (ctx->scheduler) {
        engagement* eng = engagement_find(ctx->engagements, engagement_id);
        if (eng) {
            (void)engagement_scheduler_register(ctx->scheduler, eng);
        }
    }
    op->engagement_id = engagement_id;
    if (op->repeat_interval == 0u) {
        op->status = INTERDICTION_STATUS_RESOLVED;
        op->next_due_tick = DOM_TIME_ACT_MAX;
    } else {
        op->next_due_tick = op->schedule_act + op->repeat_interval;
        op->schedule_act = op->next_due_tick;
    }
    return 0;
}
