/*
Shared helpers for control-layer tests (TESTX2).
*/
#ifndef DOMINIUM_TEST_CONTROL_COMMON_H
#define DOMINIUM_TEST_CONTROL_COMMON_H

#include "dominium/session/mp0_session.h"
#include "tests/test_version.h"

#include <stdio.h>
#include <string.h>

static int mp0_build_state(dom_mp0_state* state)
{
    if (dom_mp0_state_init(state, 0) != 0) {
        return 0;
    }
    state->consumption.params.consumption_interval = 5;
    state->consumption.params.hunger_max = 2;
    state->consumption.params.thirst_max = 2;
    if (dom_mp0_register_cohort(state, 1u, 1u, 100u, 101u, 201u, 301u) != 0) {
        return 0;
    }
    if (dom_mp0_register_cohort(state, 2u, 1u, 100u, 102u, 202u, 302u) != 0) {
        return 0;
    }
    if (dom_mp0_set_needs(state, 1u, 0u, 0u, 1u) != 0) {
        return 0;
    }
    if (dom_mp0_set_needs(state, 2u, 5u, 5u, 1u) != 0) {
        return 0;
    }
    if (dom_mp0_bind_controller(state, 1u, 101u) != 0) {
        return 0;
    }
    return 1;
}

static int mp0_build_commands(dom_mp0_command_queue* queue, dom_mp0_command* storage)
{
    survival_production_action_input gather;
    life_cmd_continuation_select cont;

    dom_mp0_command_queue_init(queue, storage, DOM_MP0_MAX_COMMANDS);
    memset(&gather, 0, sizeof(gather));
    gather.cohort_id = 2u;
    gather.type = SURVIVAL_ACTION_GATHER_FOOD;
    gather.start_tick = 0;
    gather.duration_ticks = 5;
    gather.output_food = 4u;
    gather.provenance_ref = 900u;
    if (dom_mp0_command_add_production(queue, 0, &gather) != 0) {
        return 0;
    }

    memset(&cont, 0, sizeof(cont));
    cont.controller_id = 1u;
    cont.policy_id = LIFE_POLICY_S1;
    cont.target_person_id = 102u;
    cont.action = LIFE_CONT_ACTION_TRANSFER;
    if (dom_mp0_command_add_continuation(queue, 15, &cont) != 0) {
        return 0;
    }
    dom_mp0_command_sort(queue);
    return 1;
}

static int mp0_run_hash(u64* out_hash)
{
    dom_mp0_state state;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];

    if (!out_hash) {
        return 0;
    }
    if (!mp0_build_commands(&queue, storage)) {
        return 0;
    }
    if (!mp0_build_state(&state)) {
        return 0;
    }
    if (dom_mp0_run(&state, &queue, 30) != 0) {
        return 0;
    }
    *out_hash = dom_mp0_hash_state(&state);
    return 1;
}

#endif /* DOMINIUM_TEST_CONTROL_COMMON_H */
