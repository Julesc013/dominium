/*
Minimal server entrypoint with MP0 loopback/local modes.
*/
#include "dominium/session/mp0_session.h"

#include <stdio.h>
#include <string.h>

static int mp0_build_state(dom_mp0_state* state)
{
    (void)dom_mp0_state_init(state, 0);
    state->consumption.params.consumption_interval = 5;
    state->consumption.params.hunger_max = 2;
    state->consumption.params.thirst_max = 2;
    if (dom_mp0_register_cohort(state, 1u, 1u, 100u, 101u, 201u, 301u) != 0) {
        return -1;
    }
    if (dom_mp0_register_cohort(state, 2u, 1u, 100u, 102u, 202u, 302u) != 0) {
        return -2;
    }
    if (dom_mp0_set_needs(state, 1u, 0u, 0u, 1u) != 0) {
        return -3;
    }
    if (dom_mp0_set_needs(state, 2u, 5u, 5u, 1u) != 0) {
        return -4;
    }
    if (dom_mp0_bind_controller(state, 1u, 101u) != 0) {
        return -5;
    }
    return 0;
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
        return -1;
    }

    memset(&cont, 0, sizeof(cont));
    cont.controller_id = 1u;
    cont.policy_id = LIFE_POLICY_S1;
    cont.target_person_id = 102u;
    cont.action = LIFE_CONT_ACTION_TRANSFER;
    if (dom_mp0_command_add_continuation(queue, 15, &cont) != 0) {
        return -2;
    }
    dom_mp0_command_sort(queue);
    return 0;
}

static int mp0_run_server_auth(void)
{
    dom_mp0_state server;
    dom_mp0_state client;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];
    u64 hash_server;
    u64 hash_client;

    if (mp0_build_commands(&queue, storage) != 0) {
        return 1;
    }
    if (mp0_build_state(&server) != 0) {
        return 1;
    }
    if (mp0_build_state(&client) != 0) {
        return 1;
    }
    (void)dom_mp0_run(&server, &queue, 30);
    dom_mp0_copy_authoritative(&server, &client);
    hash_server = dom_mp0_hash_state(&server);
    hash_client = dom_mp0_hash_state(&client);
    printf("MP0 server-auth hash: %llu (client %llu)\n",
           (unsigned long long)hash_server,
           (unsigned long long)hash_client);
    return (hash_server == hash_client) ? 0 : 1;
}

static int mp0_run_loopback(void)
{
    dom_mp0_state state;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];
    u64 hash_state;

    if (mp0_build_commands(&queue, storage) != 0) {
        return 1;
    }
    if (mp0_build_state(&state) != 0) {
        return 1;
    }
    (void)dom_mp0_run(&state, &queue, 30);
    hash_state = dom_mp0_hash_state(&state);
    printf("MP0 loopback hash: %llu\n", (unsigned long long)hash_state);
    return 0;
}

int main(int argc, char** argv)
{
    int i;
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--mp0-loopback") == 0) {
            return mp0_run_loopback();
        }
        if (strcmp(argv[i], "--mp0-server-auth") == 0) {
            return mp0_run_server_auth();
        }
    }
    printf("Dominium server stub. Use --mp0-loopback or --mp0-server-auth.\\n");
    return 0;
}
