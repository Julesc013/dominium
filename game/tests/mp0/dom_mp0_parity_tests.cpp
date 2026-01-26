/*
MP0 offline + local multiplayer parity tests.
*/
#include "dominium/session/mp0_session.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int build_base_state(dom_mp0_state* state)
{
    (void)dom_mp0_state_init(state, 0);
    state->consumption.params.consumption_interval = 5;
    state->consumption.params.hunger_max = 2;
    state->consumption.params.thirst_max = 2;

    EXPECT(dom_mp0_register_cohort(state, 1u, 1u, 100u, 101u, 201u, 301u) == 0, "register cohort 1");
    EXPECT(dom_mp0_register_cohort(state, 2u, 1u, 100u, 102u, 202u, 302u) == 0, "register cohort 2");

    EXPECT(dom_mp0_set_needs(state, 1u, 0u, 0u, 1u) == 0, "needs cohort1");
    EXPECT(dom_mp0_set_needs(state, 2u, 5u, 5u, 1u) == 0, "needs cohort2");

    EXPECT(dom_mp0_bind_controller(state, 1u, 101u) == 0, "bind controller");
    return 0;
}

static int build_command_script(dom_mp0_command_queue* queue)
{
    survival_production_action_input gather;
    life_cmd_continuation_select cont;

    memset(&gather, 0, sizeof(gather));
    gather.cohort_id = 2u;
    gather.type = SURVIVAL_ACTION_GATHER_FOOD;
    gather.start_tick = 0;
    gather.duration_ticks = 5;
    gather.output_food = 4u;
    gather.provenance_ref = 900u;
    EXPECT(dom_mp0_command_add_production(queue, 0, &gather) == 0, "add production");

    memset(&cont, 0, sizeof(cont));
    cont.controller_id = 1u;
    cont.policy_id = LIFE_POLICY_S1;
    cont.target_person_id = 102u;
    cont.action = LIFE_CONT_ACTION_TRANSFER;
    EXPECT(dom_mp0_command_add_continuation(queue, 15, &cont) == 0, "add continuation");

    dom_mp0_command_sort(queue);
    return 0;
}

static int test_offline_loopback_equivalence(void)
{
    static dom_mp0_state a;
    static dom_mp0_state b;
    dom_mp0_command commands_storage[DOM_MP0_MAX_COMMANDS];
    dom_mp0_command_queue queue;
    u64 hash_a;
    u64 hash_b;

    dom_mp0_command_queue_init(&queue, commands_storage, DOM_MP0_MAX_COMMANDS);
    EXPECT(build_command_script(&queue) == 0, "build command script");

    EXPECT(build_base_state(&a) == 0, "build state A");
    EXPECT(build_base_state(&b) == 0, "build state B");
    EXPECT(dom_mp0_run(&a, &queue, 30) == 0, "run A");
    EXPECT(dom_mp0_run(&b, &queue, 30) == 0, "run B");

    hash_a = dom_mp0_hash_state(&a);
    hash_b = dom_mp0_hash_state(&b);
    EXPECT(hash_a == hash_b, "loopback hash mismatch");
    return 0;
}

static int test_lockstep_parity(void)
{
    static dom_mp0_state peer_a;
    static dom_mp0_state peer_b;
    dom_mp0_command commands_storage[DOM_MP0_MAX_COMMANDS];
    dom_mp0_command_queue queue;
    u64 hash_a;
    u64 hash_b;

    dom_mp0_command_queue_init(&queue, commands_storage, DOM_MP0_MAX_COMMANDS);
    EXPECT(build_command_script(&queue) == 0, "build command script");

    EXPECT(build_base_state(&peer_a) == 0, "build state A");
    EXPECT(build_base_state(&peer_b) == 0, "build state B");
    EXPECT(dom_mp0_run(&peer_a, &queue, 30) == 0, "lockstep run A");
    EXPECT(dom_mp0_run(&peer_b, &queue, 30) == 0, "lockstep run B");

    hash_a = dom_mp0_hash_state(&peer_a);
    hash_b = dom_mp0_hash_state(&peer_b);
    EXPECT(hash_a == hash_b, "lockstep hash mismatch");
    EXPECT(hash_a != 0u, "hash should be non-zero");
    return 0;
}

static int test_server_auth_parity(void)
{
    static dom_mp0_state server;
    static dom_mp0_state client;
    dom_mp0_command commands_storage[DOM_MP0_MAX_COMMANDS];
    dom_mp0_command_queue queue;
    u64 hash_server;
    u64 hash_client;

    dom_mp0_command_queue_init(&queue, commands_storage, DOM_MP0_MAX_COMMANDS);
    EXPECT(build_command_script(&queue) == 0, "build command script");

    EXPECT(build_base_state(&server) == 0, "build state server");
    EXPECT(build_base_state(&client) == 0, "build state client");

    EXPECT(dom_mp0_run(&server, &queue, 30) == 0, "server run");
    dom_mp0_copy_authoritative(&server, &client);

    hash_server = dom_mp0_hash_state(&server);
    hash_client = dom_mp0_hash_state(&client);
    EXPECT(hash_server == hash_client, "server-auth hash mismatch");
    return 0;
}

int main(void)
{
    if (test_offline_loopback_equivalence() != 0) return 1;
    if (test_lockstep_parity() != 0) return 1;
    if (test_server_auth_parity() != 0) return 1;
    return 0;
}
