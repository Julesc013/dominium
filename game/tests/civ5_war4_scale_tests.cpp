/*
CIV5 WAR4 scale warfare tests.
*/
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/logistics/transport_capacity.h"
#include "dominium/rules/war/blockade.h"
#include "dominium/rules/war/interdiction.h"
#include "dominium/rules/war/route_control.h"
#include "dominium/rules/war/siege_effects.h"
#include "dominium/rules/war/war_scale_scheduler.h"
#include "dominium/rules/war/security_force.h"
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/needs_model.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct war4_test_context {
    route_control route_storage[8];
    route_control_registry routes;

    blockade_state blockade_storage[8];
    blockade_registry blockades;

    interdiction_operation interdiction_storage[8];
    interdiction_registry interdictions;

    siege_state siege_storage[8];
    siege_registry sieges;

    engagement engagement_storage[8];
    engagement_registry engagements;

    security_force force_storage[4];
    security_force_registry forces;

    legitimacy_state legitimacy_storage[4];
    legitimacy_registry legitimacy;

    infra_store store_storage[4];
    infra_store_registry stores;

    survival_cohort cohort_storage[4];
    survival_cohort_registry cohorts;

    survival_needs_entry needs_storage[4];
    survival_needs_registry needs;

    survival_needs_params needs_params;

    dom_time_event due_events[32];
    dg_due_entry due_entries[32];
    war_scale_due_user due_users[32];
    war_scale_scheduler scheduler;
} war4_test_context;

static void war4_context_init(war4_test_context* t)
{
    blockade_update_context blockade_ctx;
    interdiction_context interdiction_ctx;
    siege_update_context siege_ctx;

    memset(t, 0, sizeof(*t));
    route_control_registry_init(&t->routes, t->route_storage, 8u);
    blockade_registry_init(&t->blockades, t->blockade_storage, 8u, 1u);
    interdiction_registry_init(&t->interdictions, t->interdiction_storage, 8u, 1u);
    siege_registry_init(&t->sieges, t->siege_storage, 8u, 1u);
    engagement_registry_init(&t->engagements, t->engagement_storage, 8u, 1u);
    security_force_registry_init(&t->forces, t->force_storage, 4u, 1u);
    legitimacy_registry_init(&t->legitimacy, t->legitimacy_storage, 4u);
    infra_store_registry_init(&t->stores, t->store_storage, 4u);
    survival_cohort_registry_init(&t->cohorts, t->cohort_storage, 4u);
    survival_needs_registry_init(&t->needs, t->needs_storage, 4u);
    survival_needs_params_default(&t->needs_params);

    memset(&blockade_ctx, 0, sizeof(blockade_ctx));
    blockade_ctx.stores = &t->stores;
    blockade_ctx.legitimacy = &t->legitimacy;
    blockade_ctx.now_act = 0u;

    memset(&interdiction_ctx, 0, sizeof(interdiction_ctx));
    interdiction_ctx.routes = &t->routes;
    interdiction_ctx.forces = &t->forces;
    interdiction_ctx.engagements = &t->engagements;
    interdiction_ctx.scheduler = 0;

    memset(&siege_ctx, 0, sizeof(siege_ctx));
    siege_ctx.legitimacy = &t->legitimacy;
    siege_ctx.needs = &t->needs;
    siege_ctx.cohorts = &t->cohorts;
    siege_ctx.needs_params = t->needs_params;
    siege_ctx.now_act = 0u;

    (void)war_scale_scheduler_init(&t->scheduler,
                                   t->due_events,
                                   32u,
                                   t->due_entries,
                                   t->due_users,
                                   32u,
                                   0u,
                                   &t->blockades,
                                   &t->interdictions,
                                   &t->sieges,
                                   &blockade_ctx,
                                   &interdiction_ctx,
                                   &siege_ctx);
}

static int war4_seed_route(war4_test_context* t, u64 route_id)
{
    return route_control_register(&t->routes, route_id, 0u, 500u, ROUTE_ACCESS_ALLOW);
}

static int war4_seed_force(war4_test_context* t, u64 force_id)
{
    return security_force_register(&t->forces, force_id, 1u, 1u, 1u, force_id);
}

static int war4_seed_legitimacy(war4_test_context* t, u64 legit_id, u32 value)
{
    return legitimacy_register(&t->legitimacy, legit_id, value, LEGITIMACY_SCALE,
                               700u, 400u, 100u);
}

static int war4_seed_store(war4_test_context* t, u64 store_id, u64 asset_id, u32 qty)
{
    if (infra_store_register(&t->stores, store_id) != 0) {
        return -1;
    }
    if (qty > 0u) {
        if (infra_store_add(&t->stores, store_id, asset_id, qty) != 0) {
            return -2;
        }
    }
    return 0;
}

static int war4_seed_cohort(war4_test_context* t, u64 cohort_id, u32 count)
{
    return survival_cohort_register(&t->cohorts, cohort_id, count, 1u);
}

static int war4_seed_needs(war4_test_context* t,
                           u64 cohort_id,
                           u32 food,
                           u32 water,
                           u32 shelter,
                           u32 hunger,
                           u32 thirst)
{
    survival_needs_state state;
    memset(&state, 0, sizeof(state));
    state.food_store = food;
    state.water_store = water;
    state.shelter_level = shelter;
    state.hunger_level = hunger;
    state.thirst_level = thirst;
    return survival_needs_register(&t->needs, cohort_id, &state);
}

static int test_blockade_effects_deterministic(void)
{
    blockade_state a;
    blockade_state b;
    logistics_flow_input input;
    blockade_flow_effect ea;
    blockade_flow_effect eb;

    memset(&a, 0, sizeof(a));
    memset(&b, 0, sizeof(b));
    a.blockade_id = 1u;
    a.domain_ref = 10u;
    a.blockading_force_count = 1u;
    a.control_strength = 600u;
    a.policy = BLOCKADE_POLICY_INSPECT;
    a.inspect_delay_ticks = 3u;
    a.status = BLOCKADE_STATUS_ACTIVE;
    b = a;

    memset(&input, 0, sizeof(input));
    input.flow_id = 1u;
    input.src_store_ref = 100u;
    input.dst_store_ref = 200u;
    input.asset_id = 55u;
    input.qty = 10u;
    input.departure_act = 0u;
    input.arrival_act = 10u;
    input.capacity_ref = 500u;

    EXPECT(blockade_apply_to_flow(&a, 10u, &input, &ea, 0) == 0, "apply blockade a");
    EXPECT(blockade_apply_to_flow(&b, 10u, &input, &eb, 0) == 0, "apply blockade b");
    EXPECT(ea.deny == eb.deny, "deny mismatch");
    EXPECT(ea.adjusted_qty == eb.adjusted_qty, "qty mismatch");
    EXPECT(ea.adjusted_arrival_act == eb.adjusted_arrival_act, "arrival mismatch");
    return 0;
}

static int test_interdiction_scheduling_determinism(void)
{
    war4_test_context a;
    war4_test_context b;
    interdiction_operation op_a;
    interdiction_operation op_b;

    war4_context_init(&a);
    war4_context_init(&b);
    EXPECT(war4_seed_route(&a, 5u) == 0, "route a");
    EXPECT(war4_seed_route(&b, 5u) == 0, "route b");
    EXPECT(war4_seed_force(&a, 11u) == 0, "force a attacker");
    EXPECT(war4_seed_force(&a, 12u) == 0, "force a defender");
    EXPECT(war4_seed_force(&b, 11u) == 0, "force b attacker");
    EXPECT(war4_seed_force(&b, 12u) == 0, "force b defender");

    memset(&op_a, 0, sizeof(op_a));
    op_a.interdiction_id = 1u;
    op_a.route_id = 5u;
    op_a.attacker_force_ref = 11u;
    op_a.defender_force_ref = 12u;
    op_a.domain_scope = 2u;
    op_a.schedule_act = 10u;
    op_a.resolution_delay = 5u;
    op_a.next_due_tick = 10u;
    op_a.status = INTERDICTION_STATUS_SCHEDULED;
    op_b = op_a;

    EXPECT(interdiction_register(&a.interdictions, &op_a, 0) == 0, "register a");
    EXPECT(interdiction_register(&b.interdictions, &op_b, 0) == 0, "register b");
    EXPECT(war_scale_scheduler_register_interdiction(&a.scheduler, &a.interdictions.operations[0]) == 0,
           "sched a");
    EXPECT(war_scale_scheduler_register_interdiction(&b.scheduler, &b.interdictions.operations[0]) == 0,
           "sched b");
    EXPECT(war_scale_scheduler_advance(&a.scheduler, 10u) == 0, "advance a");
    EXPECT(war_scale_scheduler_advance(&b.scheduler, 10u) == 0, "advance b");

    EXPECT(a.interdictions.operations[0].engagement_id == b.interdictions.operations[0].engagement_id,
           "engagement id mismatch");
    EXPECT(a.interdictions.operations[0].status == b.interdictions.operations[0].status,
           "status mismatch");
    return 0;
}

static int test_siege_deprivation_batch_vs_step(void)
{
    war4_test_context step;
    war4_test_context batch;
    siege_state siege;
    siege_state* s_step;
    siege_state* s_batch;
    u32 legit_step;
    u32 legit_batch;

    war4_context_init(&step);
    war4_context_init(&batch);
    EXPECT(war4_seed_legitimacy(&step, 9u, 800u) == 0, "legitimacy step");
    EXPECT(war4_seed_legitimacy(&batch, 9u, 800u) == 0, "legitimacy batch");
    EXPECT(war4_seed_cohort(&step, 77u, 10u) == 0, "cohort step");
    EXPECT(war4_seed_cohort(&batch, 77u, 10u) == 0, "cohort batch");
    EXPECT(war4_seed_needs(&step, 77u, 0u, 0u, 0u, 4u, 3u) == 0, "needs step");
    EXPECT(war4_seed_needs(&batch, 77u, 0u, 0u, 0u, 4u, 3u) == 0, "needs batch");

    memset(&siege, 0, sizeof(siege));
    siege.siege_id = 1u;
    siege.target_domain_ref = 42u;
    siege.population_cohort_id = 77u;
    siege.legitimacy_id = 9u;
    siege.deprivation_threshold = 200u;
    siege.legitimacy_delta = -5;
    siege.update_interval = 5u;
    siege.next_due_tick = 5u;
    siege.status = SIEGE_STATUS_ACTIVE;

    EXPECT(siege_register(&step.sieges, &siege, 0) == 0, "register step");
    EXPECT(siege_register(&batch.sieges, &siege, 0) == 0, "register batch");

    s_step = siege_find(&step.sieges, 1u);
    s_batch = siege_find(&batch.sieges, 1u);
    EXPECT(s_step && s_batch, "find siege");

    EXPECT(war_scale_scheduler_register_siege(&step.scheduler, s_step) == 0, "sched step");
    EXPECT(war_scale_scheduler_register_siege(&batch.scheduler, s_batch) == 0, "sched batch");

    EXPECT(war_scale_scheduler_advance(&step.scheduler, 5u) == 0, "step 5");
    EXPECT(war_scale_scheduler_advance(&step.scheduler, 10u) == 0, "step 10");
    EXPECT(war_scale_scheduler_advance(&batch.scheduler, 10u) == 0, "batch 10");

    legit_step = step.legitimacy.states[0].value;
    legit_batch = batch.legitimacy.states[0].value;
    EXPECT(legit_step == legit_batch, "legitimacy mismatch");
    EXPECT(s_step->deprivation_pressure == s_batch->deprivation_pressure, "pressure mismatch");
    return 0;
}

static int test_no_global_iteration(void)
{
    war4_test_context t;
    blockade_state blk;
    interdiction_operation op;
    siege_state siege;
    blockade_state* bstate;
    interdiction_operation* istate;
    siege_state* sstate;

    war4_context_init(&t);
    EXPECT(war4_seed_route(&t, 1u) == 0, "route");
    EXPECT(war4_seed_force(&t, 11u) == 0, "force a");
    EXPECT(war4_seed_force(&t, 12u) == 0, "force b");
    EXPECT(war4_seed_legitimacy(&t, 9u, 800u) == 0, "legitimacy");
    EXPECT(war4_seed_cohort(&t, 77u, 10u) == 0, "cohort");
    EXPECT(war4_seed_needs(&t, 77u, 0u, 0u, 0u, 4u, 3u) == 0, "needs");

    memset(&blk, 0, sizeof(blk));
    blk.blockade_id = 1u;
    blk.domain_ref = 99u;
    blk.blockading_force_count = 1u;
    blk.status = BLOCKADE_STATUS_ACTIVE;
    blk.next_due_tick = 5u;
    blk.maintenance_interval = 10u;
    EXPECT(blockade_register(&t.blockades, &blk, 0, 0) == 0, "blockade register");

    memset(&op, 0, sizeof(op));
    op.interdiction_id = 2u;
    op.route_id = 1u;
    op.attacker_force_ref = 11u;
    op.defender_force_ref = 12u;
    op.schedule_act = 50u;
    op.resolution_delay = 5u;
    op.next_due_tick = 50u;
    op.status = INTERDICTION_STATUS_SCHEDULED;
    EXPECT(interdiction_register(&t.interdictions, &op, 0) == 0, "interdiction register");

    memset(&siege, 0, sizeof(siege));
    siege.siege_id = 3u;
    siege.target_domain_ref = 42u;
    siege.population_cohort_id = 77u;
    siege.legitimacy_id = 9u;
    siege.update_interval = 50u;
    siege.next_due_tick = 50u;
    siege.status = SIEGE_STATUS_ACTIVE;
    EXPECT(siege_register(&t.sieges, &siege, 0) == 0, "siege register");

    bstate = blockade_find(&t.blockades, 1u);
    istate = interdiction_find(&t.interdictions, 2u);
    sstate = siege_find(&t.sieges, 3u);
    EXPECT(bstate && istate && sstate, "find states");

    EXPECT(war_scale_scheduler_register_blockade(&t.scheduler, bstate) == 0, "sched blockade");
    EXPECT(war_scale_scheduler_register_interdiction(&t.scheduler, istate) == 0, "sched interdiction");
    EXPECT(war_scale_scheduler_register_siege(&t.scheduler, sstate) == 0, "sched siege");

    EXPECT(war_scale_scheduler_advance(&t.scheduler, 5u) == 0, "advance");
    EXPECT(t.scheduler.processed_last == 1u, "processed count");
    return 0;
}

static int test_shard_message_ordering(void)
{
    route_control_message_queue a;
    route_control_message_queue b;
    route_control_message storage_a[6];
    route_control_message storage_b[6];
    route_control_message msg[3];
    u32 i;

    route_control_message_queue_init(&a, storage_a, 6u, 1u);
    route_control_message_queue_init(&b, storage_b, 6u, 1u);

    memset(msg, 0, sizeof(msg));
    msg[0].route_id = 10u;
    msg[0].arrival_act = 20u;
    msg[0].order_key = 2u;
    msg[1].route_id = 11u;
    msg[1].arrival_act = 10u;
    msg[1].order_key = 1u;
    msg[2].route_id = 12u;
    msg[2].arrival_act = 20u;
    msg[2].order_key = 1u;

    EXPECT(route_control_message_queue_push(&a, &msg[0], 0) == 0, "push a0");
    EXPECT(route_control_message_queue_push(&a, &msg[1], 0) == 0, "push a1");
    EXPECT(route_control_message_queue_push(&a, &msg[2], 0) == 0, "push a2");

    EXPECT(route_control_message_queue_push(&b, &msg[2], 0) == 0, "push b2");
    EXPECT(route_control_message_queue_push(&b, &msg[0], 0) == 0, "push b0");
    EXPECT(route_control_message_queue_push(&b, &msg[1], 0) == 0, "push b1");

    EXPECT(a.count == b.count, "queue count mismatch");
    for (i = 0u; i < a.count; ++i) {
        const route_control_message* ma = route_control_message_at(&a, i);
        const route_control_message* mb = route_control_message_at(&b, i);
        EXPECT(ma && mb, "message missing");
        EXPECT(ma->route_id == mb->route_id, "route ordering mismatch");
        EXPECT(ma->arrival_act == mb->arrival_act, "arrival ordering mismatch");
        EXPECT(ma->order_key == mb->order_key, "order key mismatch");
    }
    return 0;
}

int main(void)
{
    if (test_blockade_effects_deterministic() != 0) return 1;
    if (test_interdiction_scheduling_determinism() != 0) return 1;
    if (test_siege_deprivation_batch_vs_step() != 0) return 1;
    if (test_no_global_iteration() != 0) return 1;
    if (test_shard_message_ordering() != 0) return 1;
    return 0;
}
