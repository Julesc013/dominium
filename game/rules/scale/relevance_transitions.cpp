/*
FILE: game/rules/scale/relevance_transitions.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale rules
RESPONSIBILITY: Implements interest relevance transition helpers for Work IR tasks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: All transitions and ordering are deterministic.
*/
#include "dominium/rules/scale/relevance_transitions.h"

#include "dominium/interest_sources.h"

extern "C" {

void dom_interest_runtime_reset(dom_interest_runtime_state* state)
{
    u32 i;
    if (!state) {
        return;
    }
    if (state->scratch_set) {
        dom_interest_set_clear(state->scratch_set);
    }
    state->transition_count = 0u;
    state->request_count = 0u;
    for (i = 0u; i < DOM_INTEREST_SOURCE_COUNT; ++i) {
        state->source_cursor[i] = 0u;
    }
}

void dom_interest_runtime_advance_cursor(dom_interest_runtime_state* state,
                                         dom_interest_source_kind source_kind,
                                         u32 count)
{
    if (!state) {
        return;
    }
    if (source_kind >= DOM_INTEREST_SOURCE_COUNT) {
        return;
    }
    state->source_cursor[source_kind] += count;
}

static int dom_interest_emit_slice(dom_interest_set* set,
                                   const dom_interest_source_list* list,
                                   dom_interest_reason reason,
                                   u32 start_index,
                                   u32 count,
                                   dom_act_time_t now_tick)
{
    dom_interest_source_list slice;
    if (!set || !list || !list->ids) {
        return -1;
    }
    if (start_index >= list->count || count == 0u) {
        return 0;
    }
    if (start_index + count > list->count) {
        count = list->count - start_index;
    }
    slice = *list;
    slice.ids = list->ids + start_index;
    slice.count = count;

    switch (reason) {
        case DOM_INTEREST_REASON_PLAYER_FOCUS:
            return dom_interest_emit_player_focus(set, &slice, now_tick);
        case DOM_INTEREST_REASON_COMMAND_INTENT:
            return dom_interest_emit_command_intent(set, &slice, now_tick);
        case DOM_INTEREST_REASON_LOGISTICS_ROUTE:
            return dom_interest_emit_logistics(set, &slice, now_tick);
        case DOM_INTEREST_REASON_SENSOR_COMMS:
            return dom_interest_emit_sensor_comms(set, &slice, now_tick);
        case DOM_INTEREST_REASON_HAZARD_CONFLICT:
            return dom_interest_emit_hazard_conflict(set, &slice, now_tick);
        case DOM_INTEREST_REASON_GOVERNANCE_SCOPE:
            return dom_interest_emit_governance_scope(set, &slice, now_tick);
        default:
            return -2;
    }
}

int dom_interest_collect_slice(dom_interest_runtime_state* state,
                               const dom_interest_source_list* list,
                               dom_interest_reason reason,
                               u32 start_index,
                               u32 count,
                               dom_act_time_t now_tick)
{
    if (!state || !state->scratch_set) {
        return -1;
    }
    return dom_interest_emit_slice(state->scratch_set, list, reason, start_index, count, now_tick);
}

int dom_interest_merge_sets(dom_interest_runtime_state* state)
{
    u32 i;
    if (!state || !state->scratch_set || !state->merged_set) {
        return -1;
    }
    dom_interest_set_finalize(state->scratch_set);
    dom_interest_set_clear(state->merged_set);
    for (i = 0u; i < state->scratch_set->count; ++i) {
        const dom_interest_entry* entry = &state->scratch_set->entries[i];
        (void)dom_interest_set_add(state->merged_set,
                                   entry->target_kind,
                                   entry->target_id,
                                   (dom_interest_reason)entry->reason,
                                   entry->strength,
                                   entry->expiry_tick);
    }
    dom_interest_set_finalize(state->merged_set);
    return (int)state->merged_set->count;
}

u32 dom_interest_apply_hysteresis(dom_interest_runtime_state* state,
                                  const dom_interest_policy* policy,
                                  dom_act_time_t now_tick)
{
    u32 cap;
    if (!state || !state->merged_set || !state->relevance_states) {
        return 0u;
    }
    cap = state->transition_capacity;
    state->transition_count = cap;
    dom_interest_state_apply(state->merged_set,
                             state->relevance_states,
                             state->relevance_count,
                             policy,
                             now_tick,
                             state->transitions,
                             &state->transition_count);
    return state->transition_count;
}

u32 dom_interest_build_fidelity_requests(dom_interest_runtime_state* state,
                                         dom_fidelity_tier refine_tier,
                                         dom_fidelity_tier collapse_tier,
                                         u32 reason)
{
    u32 i;
    if (!state || !state->fidelity_requests || !state->transitions) {
        return 0u;
    }
    state->request_count = 0u;
    for (i = 0u; i < state->transition_count; ++i) {
        dom_fidelity_request* req;
        const dom_interest_transition* trans = &state->transitions[i];
        if (state->request_count >= state->request_capacity) {
            break;
        }
        req = &state->fidelity_requests[state->request_count++];
        req->object_id = trans->target_id;
        req->object_kind = trans->target_kind;
        if (trans->to_state == DOM_REL_HOT || trans->to_state == DOM_REL_WARM) {
            req->type = DOM_FIDELITY_REQUEST_REFINE;
            req->target_tier = refine_tier;
        } else {
            req->type = DOM_FIDELITY_REQUEST_COLLAPSE;
            req->target_tier = collapse_tier;
        }
        req->reason = reason;
    }
    return state->request_count;
}

} /* extern "C" */
