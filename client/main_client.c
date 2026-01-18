/*
Minimal client entrypoint with MP0 local-connect demo.
*/
#include "dominium/session/mp0_session.h"

#include <stdio.h>
#include <string.h>

static int mp0_run_local_client(void)
{
    dom_mp0_state state;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];
    survival_production_action_input gather;
    life_cmd_continuation_select cont;
    u64 hash_state;

    dom_mp0_command_queue_init(&queue, storage, DOM_MP0_MAX_COMMANDS);
    memset(&gather, 0, sizeof(gather));
    gather.cohort_id = 2u;
    gather.type = SURVIVAL_ACTION_GATHER_FOOD;
    gather.start_tick = 0;
    gather.duration_ticks = 5;
    gather.output_food = 4u;
    gather.provenance_ref = 900u;
    (void)dom_mp0_command_add_production(&queue, 0, &gather);
    memset(&cont, 0, sizeof(cont));
    cont.controller_id = 1u;
    cont.policy_id = LIFE_POLICY_S1;
    cont.target_person_id = 102u;
    cont.action = LIFE_CONT_ACTION_TRANSFER;
    (void)dom_mp0_command_add_continuation(&queue, 15, &cont);
    dom_mp0_command_sort(&queue);

    (void)dom_mp0_state_init(&state, 0);
    state.consumption.params.consumption_interval = 5;
    state.consumption.params.hunger_max = 2;
    state.consumption.params.thirst_max = 2;
    (void)dom_mp0_register_cohort(&state, 1u, 1u, 100u, 101u, 201u, 301u);
    (void)dom_mp0_register_cohort(&state, 2u, 1u, 100u, 102u, 202u, 302u);
    (void)dom_mp0_set_needs(&state, 1u, 0u, 0u, 1u);
    (void)dom_mp0_set_needs(&state, 2u, 5u, 5u, 1u);
    (void)dom_mp0_bind_controller(&state, 1u, 101u);
    (void)dom_mp0_run(&state, &queue, 30);
    hash_state = dom_mp0_hash_state(&state);
    printf("MP0 client local hash: %llu\n", (unsigned long long)hash_state);
    return 0;
}

int main(int argc, char** argv)
{
    int i;
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--mp0-connect=local") == 0) {
            return mp0_run_local_client();
        }
    }
    printf("Dominium client stub. Use --mp0-connect=local.\\n");
    return 0;
}
