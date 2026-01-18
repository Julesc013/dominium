/*
FILE: game/core/session/mp0_session.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / session
RESPONSIBILITY: Implements MP0 loopback/lockstep/server-auth parity harness.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: State transitions are deterministic and replayable.
*/
#include "dominium/session/mp0_session.h"

#include <string.h>

static u64 dom_mp0_hash_mix(u64 h, u64 v)
{
    const u64 prime = 1099511628211ULL;
    h ^= v;
    h *= prime;
    return h;
}

void dom_mp0_command_queue_init(dom_mp0_command_queue* queue,
                                dom_mp0_command* storage,
                                u32 capacity)
{
    if (!queue) {
        return;
    }
    queue->commands = storage;
    queue->count = 0u;
    queue->capacity = capacity;
    queue->next_sequence = 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_mp0_command) * (size_t)capacity);
    }
}

int dom_mp0_command_add_production(dom_mp0_command_queue* queue,
                                   dom_act_time_t tick,
                                   const survival_production_action_input* input)
{
    dom_mp0_command* cmd;
    if (!queue || !queue->commands || !input) {
        return -1;
    }
    if (queue->count >= queue->capacity) {
        return -2;
    }
    cmd = &queue->commands[queue->count++];
    memset(cmd, 0, sizeof(*cmd));
    cmd->type = DOM_MP0_CMD_PRODUCTION;
    cmd->tick = tick;
    cmd->sequence = queue->next_sequence++;
    cmd->data.production = *input;
    return 0;
}

int dom_mp0_command_add_continuation(dom_mp0_command_queue* queue,
                                     dom_act_time_t tick,
                                     const life_cmd_continuation_select* cmd_in)
{
    dom_mp0_command* cmd;
    if (!queue || !queue->commands || !cmd_in) {
        return -1;
    }
    if (queue->count >= queue->capacity) {
        return -2;
    }
    cmd = &queue->commands[queue->count++];
    memset(cmd, 0, sizeof(*cmd));
    cmd->type = DOM_MP0_CMD_CONTINUATION;
    cmd->tick = tick;
    cmd->sequence = queue->next_sequence++;
    cmd->data.continuation = *cmd_in;
    return 0;
}

void dom_mp0_command_sort(dom_mp0_command_queue* queue)
{
    u32 i;
    if (!queue || !queue->commands || queue->count < 2u) {
        return;
    }
    for (i = 1u; i < queue->count; ++i) {
        dom_mp0_command key = queue->commands[i];
        u32 j = i;
        while (j > 0u) {
            const dom_mp0_command* prev = &queue->commands[j - 1u];
            if (prev->tick < key.tick) {
                break;
            }
            if (prev->tick == key.tick && prev->sequence <= key.sequence) {
                break;
            }
            queue->commands[j] = queue->commands[j - 1u];
            --j;
        }
        queue->commands[j] = key;
    }
}

static const dom_mp0_cohort_binding* dom_mp0_find_binding(const dom_mp0_state* state,
                                                          u64 cohort_id)
{
    u32 i;
    if (!state) {
        return 0;
    }
    for (i = 0u; i < state->cohort_binding_count; ++i) {
        if (state->cohort_bindings[i].cohort_id == cohort_id) {
            return &state->cohort_bindings[i];
        }
    }
    return 0;
}

static int dom_mp0_emit_death(void* user,
                              u64 cohort_id,
                              u32 count,
                              dom_act_time_t act_time,
                              u32 cause_code)
{
    dom_mp0_state* state = (dom_mp0_state*)user;
    const dom_mp0_cohort_binding* binding;
    u32 i;
    if (!state) {
        return -1;
    }
    binding = dom_mp0_find_binding(state, cohort_id);
    if (!binding) {
        return -2;
    }
    for (i = 0u; i < count; ++i) {
        life_death_input input;
        life_death_refusal_code refusal;
        memset(&input, 0, sizeof(input));
        input.body_id = binding->body_id;
        input.cause_code = (cause_code == SURVIVAL_DEATH_CAUSE_DEHYDRATION)
            ? LIFE_DEATH_CAUSE_NATURAL
            : LIFE_DEATH_CAUSE_NATURAL;
        input.act_time = act_time;
        input.location_ref = binding->location_ref;
        input.provenance_ref = 0u;
        input.policy_id = state->policy_id;
        input.remains_inventory_account_id = binding->account_id;
        input.jurisdiction_id = 0u;
        input.has_contract = 0u;
        input.allow_finder = 1u;
        input.jurisdiction_allows = 1u;
        input.estate_locked = 0u;
        input.collapse_remains = 1u;

        (void)life_handle_death(&state->death_ctx, &input, &refusal, 0, 0);
    }
    return 0;
}

int dom_mp0_state_init(dom_mp0_state* state, dom_act_time_t start_tick)
{
    survival_needs_params params;
    life_remains_decay_rules remains_rules;
    survival_death_hook death_hook;

    if (!state) {
        return -1;
    }
    memset(state, 0, sizeof(*state));
    state->now_tick = start_tick;
    state->policy_id = 1u;

    survival_cohort_registry_init(&state->cohorts, state->cohorts_storage, DOM_MP0_MAX_COHORTS);
    survival_needs_registry_init(&state->needs, state->needs_storage, DOM_MP0_MAX_COHORTS);
    survival_needs_params_default(&params);
    params.consumption_interval = 10;
    params.hunger_max = 6u;
    params.thirst_max = 4u;
    (void)survival_consumption_scheduler_init(&state->consumption,
                                              state->consumption_events,
                                              DOM_MP0_MAX_COHORTS * 4u,
                                              state->consumption_entries,
                                              state->consumption_users,
                                              DOM_MP0_MAX_COHORTS,
                                              start_tick,
                                              &state->cohorts,
                                              &state->needs,
                                              &params);
    death_hook.emit = dom_mp0_emit_death;
    death_hook.user = state;
    survival_consumption_set_death_hook(&state->consumption, &death_hook);

    survival_production_action_registry_init(&state->actions,
                                             state->actions_storage,
                                             DOM_MP0_MAX_ACTIONS,
                                             1u);
    (void)survival_production_scheduler_init(&state->production,
                                             state->production_events,
                                             DOM_MP0_MAX_ACTIONS * 2u,
                                             state->production_entries,
                                             state->production_users,
                                             DOM_MP0_MAX_ACTIONS,
                                             start_tick,
                                             &state->cohorts,
                                             &state->needs,
                                             &state->actions);

    (void)dom_ledger_init(&state->ledger);
    life_body_registry_init(&state->bodies, state->bodies_storage, DOM_MP0_MAX_PERSONS);
    life_person_registry_init(&state->persons, state->persons_storage, DOM_MP0_MAX_PERSONS);
    life_death_event_list_init(&state->death_events, state->death_events_storage,
                               DOM_MP0_MAX_DEATH_EVENTS, 1u);
    life_estate_registry_init(&state->estates, state->estates_storage, DOM_MP0_MAX_ESTATES,
                              state->estate_account_storage, DOM_MP0_MAX_ACCOUNTS, 1u);
    life_person_account_registry_init(&state->person_accounts,
                                      state->person_account_entries,
                                      DOM_MP0_MAX_PERSONS,
                                      state->person_account_storage,
                                      DOM_MP0_MAX_ACCOUNTS);
    life_account_owner_registry_init(&state->account_owners, state->owner_storage, DOM_MP0_MAX_ACCOUNTS);
    life_inheritance_action_list_init(&state->inheritance_actions,
                                      state->inheritance_storage,
                                      DOM_MP0_MAX_INHERIT_ACTIONS,
                                      1u);
    (void)life_inheritance_scheduler_init(&state->inheritance_scheduler,
                                          state->inheritance_events,
                                          DOM_MP0_MAX_INHERIT_ACTIONS * 2u,
                                          state->inheritance_entries,
                                          state->inheritance_users,
                                          DOM_MP0_MAX_INHERIT_ACTIONS,
                                          start_tick,
                                          10,
                                          &state->estates,
                                          &state->inheritance_actions);
    life_audit_log_init(&state->audit_log, state->audit_storage,
                        DOM_MP0_MAX_INHERIT_ACTIONS * 2u, 1u);
    life_controller_bindings_init(&state->bindings, state->bindings_storage, DOM_MP0_MAX_PERSONS);

    life_post_death_rights_registry_init(&state->rights, state->rights_storage,
                                         DOM_MP0_MAX_RIGHTS, 1u);
    life_remains_registry_init(&state->remains, state->remains_storage,
                               DOM_MP0_MAX_REMAINS, 1u);
    life_remains_aggregate_registry_init(&state->remains_aggregates,
                                         state->remains_aggregate_storage,
                                         DOM_MP0_MAX_REMAINS, 1u);
    remains_rules.fresh_to_decayed = 5;
    remains_rules.decayed_to_skeletal = 5;
    remains_rules.skeletal_to_unknown = 5;
    (void)life_remains_decay_scheduler_init(&state->remains_decay,
                                            state->remains_events,
                                            DOM_MP0_MAX_REMAINS * 2u,
                                            state->remains_entries,
                                            state->remains_users,
                                            DOM_MP0_MAX_REMAINS,
                                            start_tick,
                                            &state->remains,
                                            &remains_rules);

    state->death_ctx.bodies = &state->bodies;
    state->death_ctx.persons = &state->persons;
    state->death_ctx.person_accounts = &state->person_accounts;
    state->death_ctx.account_owners = &state->account_owners;
    state->death_ctx.death_events = &state->death_events;
    state->death_ctx.estates = &state->estates;
    state->death_ctx.scheduler = &state->inheritance_scheduler;
    state->death_ctx.audit_log = &state->audit_log;
    state->death_ctx.ledger = &state->ledger;
    state->death_ctx.notice_cb = 0;
    state->death_ctx.notice_user = 0;
    state->death_ctx.remains = &state->remains;
    state->death_ctx.rights = &state->rights;
    state->death_ctx.remains_decay = &state->remains_decay;
    state->death_ctx.remains_aggregates = &state->remains_aggregates;
    state->death_ctx.observation_hooks = 0;
    state->cohort_binding_count = 0u;
    return 0;
}

int dom_mp0_register_cohort(dom_mp0_state* state,
                            u64 cohort_id,
                            u32 count,
                            u64 location_ref,
                            u64 person_id,
                            u64 body_id,
                            dom_account_id_t account_id)
{
    dom_account_id_t account_ids[1];
    survival_cohort* cohort;
    survival_needs_state* needs;

    if (!state) {
        return -1;
    }
    if (state->cohort_binding_count >= DOM_MP0_MAX_COHORTS) {
        return -2;
    }
    if (life_person_register(&state->persons, person_id) != 0) {
        return -3;
    }
    if (life_body_register(&state->bodies, body_id, person_id, LIFE_BODY_ALIVE) != 0) {
        return -4;
    }
    if (dom_ledger_account_create(&state->ledger, account_id, 0u) != DOM_LEDGER_OK) {
        return -5;
    }
    account_ids[0] = account_id;
    if (life_person_account_register(&state->person_accounts, person_id, account_ids, 1u) != 0) {
        return -6;
    }
    if (survival_cohort_register(&state->cohorts, cohort_id, count, location_ref) != 0) {
        return -7;
    }
    cohort = survival_cohort_find(&state->cohorts, cohort_id);
    if (!cohort) {
        return -8;
    }
    if (survival_consumption_register_cohort(&state->consumption, cohort) != 0) {
        return -9;
    }
    needs = survival_needs_get(&state->needs, cohort_id);
    if (!needs) {
        return -10;
    }

    state->cohort_bindings[state->cohort_binding_count].cohort_id = cohort_id;
    state->cohort_bindings[state->cohort_binding_count].person_id = person_id;
    state->cohort_bindings[state->cohort_binding_count].body_id = body_id;
    state->cohort_bindings[state->cohort_binding_count].location_ref = location_ref;
    state->cohort_bindings[state->cohort_binding_count].account_id = account_id;
    state->cohort_binding_count += 1u;
    return 0;
}

int dom_mp0_set_needs(dom_mp0_state* state,
                      u64 cohort_id,
                      u32 food,
                      u32 water,
                      u32 shelter)
{
    survival_needs_state* needs;
    if (!state) {
        return -1;
    }
    needs = survival_needs_get(&state->needs, cohort_id);
    if (!needs) {
        return -2;
    }
    needs->food_store = food;
    needs->water_store = water;
    needs->shelter_level = shelter;
    return 0;
}

int dom_mp0_bind_controller(dom_mp0_state* state,
                            u64 controller_id,
                            u64 person_id)
{
    if (!state) {
        return -1;
    }
    return life_controller_bindings_set(&state->bindings, controller_id, person_id);
}

static void dom_mp0_apply_command(dom_mp0_state* state,
                                  const dom_mp0_command* cmd)
{
    if (!state || !cmd) {
        return;
    }
    if (cmd->type == DOM_MP0_CMD_PRODUCTION) {
        survival_production_refusal_code refusal;
        survival_production_action_input input = cmd->data.production;
        input.start_tick = cmd->tick;
        (void)survival_production_schedule_action(&state->production, &input, &refusal, 0);
    } else if (cmd->type == DOM_MP0_CMD_CONTINUATION) {
        (void)life_cmd_continuation_apply(&state->bindings, &cmd->data.continuation);
    }
}

static dom_act_time_t dom_mp0_min_tick(dom_act_time_t a, dom_act_time_t b)
{
    if (a == DOM_TIME_ACT_MAX) {
        return b;
    }
    if (b == DOM_TIME_ACT_MAX) {
        return a;
    }
    return (a < b) ? a : b;
}

int dom_mp0_run(dom_mp0_state* state,
                const dom_mp0_command_queue* queue,
                dom_act_time_t target_tick)
{
    u32 cmd_index = 0u;
    dom_act_time_t now;

    if (!state || !queue || !queue->commands) {
        return -1;
    }
    now = state->now_tick;
    while (now < target_tick) {
        dom_act_time_t next_cmd_tick = DOM_TIME_ACT_MAX;
        dom_act_time_t next_due;
        dom_act_time_t next_tick;

        if (cmd_index < queue->count) {
            next_cmd_tick = queue->commands[cmd_index].tick;
        }
        next_due = dom_mp0_min_tick(survival_consumption_next_due(&state->consumption),
                                    survival_production_next_due(&state->production));
        next_tick = dom_mp0_min_tick(next_cmd_tick, next_due);
        next_tick = dom_mp0_min_tick(next_tick, target_tick);
        if (next_tick == DOM_TIME_ACT_MAX) {
            break;
        }
        if (next_tick < now) {
            next_tick = now;
        }
        now = next_tick;

        while (cmd_index < queue->count && queue->commands[cmd_index].tick <= now) {
            dom_mp0_apply_command(state, &queue->commands[cmd_index]);
            cmd_index += 1u;
        }

        (void)survival_consumption_advance(&state->consumption, now);
        (void)survival_production_advance(&state->production, now);
    }
    state->now_tick = now;
    return 0;
}

u64 dom_mp0_hash_state(const dom_mp0_state* state)
{
    u64 h = 1469598103934665603ULL;
    u32 i;
    if (!state) {
        return h;
    }
    for (i = 0u; i < state->cohorts.count; ++i) {
        const survival_cohort* cohort = &state->cohorts.cohorts[i];
        h = dom_mp0_hash_mix(h, cohort->cohort_id);
        h = dom_mp0_hash_mix(h, cohort->count);
        h = dom_mp0_hash_mix(h, cohort->location_ref);
        h = dom_mp0_hash_mix(h, (u64)cohort->next_due_tick);
    }
    for (i = 0u; i < state->needs.count; ++i) {
        const survival_needs_entry* entry = &state->needs.entries[i];
        h = dom_mp0_hash_mix(h, entry->cohort_id);
        h = dom_mp0_hash_mix(h, entry->state.food_store);
        h = dom_mp0_hash_mix(h, entry->state.water_store);
        h = dom_mp0_hash_mix(h, entry->state.shelter_level);
        h = dom_mp0_hash_mix(h, entry->state.hunger_level);
        h = dom_mp0_hash_mix(h, entry->state.thirst_level);
        h = dom_mp0_hash_mix(h, (u64)entry->state.next_consumption_tick);
    }
    for (i = 0u; i < state->actions.count; ++i) {
        const survival_production_action* action = &state->actions.actions[i];
        h = dom_mp0_hash_mix(h, action->action_id);
        h = dom_mp0_hash_mix(h, action->cohort_id);
        h = dom_mp0_hash_mix(h, action->type);
        h = dom_mp0_hash_mix(h, action->status);
        h = dom_mp0_hash_mix(h, (u64)action->end_tick);
        h = dom_mp0_hash_mix(h, action->output_food);
        h = dom_mp0_hash_mix(h, action->output_water);
        h = dom_mp0_hash_mix(h, action->output_shelter);
    }
    for (i = 0u; i < state->death_events.count; ++i) {
        const life_death_event* ev = &state->death_events.events[i];
        h = dom_mp0_hash_mix(h, ev->death_event_id);
        h = dom_mp0_hash_mix(h, ev->body_id);
        h = dom_mp0_hash_mix(h, ev->person_id);
        h = dom_mp0_hash_mix(h, ev->estate_id);
        h = dom_mp0_hash_mix(h, (u64)ev->cause_code);
    }
    for (i = 0u; i < state->estates.count; ++i) {
        const life_estate* estate = &state->estates.estates[i];
        u32 count = 0u;
        const dom_account_id_t* accounts = life_estate_accounts(&state->estates, estate, &count);
        u32 j;
        h = dom_mp0_hash_mix(h, estate->estate_id);
        h = dom_mp0_hash_mix(h, estate->deceased_person_id);
        for (j = 0u; j < count; ++j) {
            h = dom_mp0_hash_mix(h, accounts[j]);
        }
    }
    for (i = 0u; i < state->bindings.count; ++i) {
        const life_controller_binding* binding = &state->bindings.bindings[i];
        h = dom_mp0_hash_mix(h, binding->controller_id);
        h = dom_mp0_hash_mix(h, binding->person_id);
    }
    for (i = 0u; i < state->ledger.account_count; ++i) {
        const dom_ledger_account* account = &state->ledger.accounts[i];
        u32 a;
        h = dom_mp0_hash_mix(h, account->account_id);
        for (a = 0u; a < account->asset_count; ++a) {
            h = dom_mp0_hash_mix(h, account->assets[a].asset_id);
            h = dom_mp0_hash_mix(h, (u64)account->assets[a].balance);
        }
    }
    return h;
}

void dom_mp0_copy_authoritative(const dom_mp0_state* src, dom_mp0_state* dst)
{
    u32 i;
    if (!src || !dst) {
        return;
    }
    dst->now_tick = src->now_tick;
    dst->policy_id = src->policy_id;

    dst->cohorts.count = src->cohorts.count;
    for (i = 0u; i < src->cohorts.count; ++i) {
        dst->cohorts.cohorts[i] = src->cohorts.cohorts[i];
    }
    dst->needs.count = src->needs.count;
    for (i = 0u; i < src->needs.count; ++i) {
        dst->needs.entries[i] = src->needs.entries[i];
    }
    dst->actions.count = src->actions.count;
    dst->actions.next_id = src->actions.next_id;
    for (i = 0u; i < src->actions.count; ++i) {
        dst->actions.actions[i] = src->actions.actions[i];
    }
    dst->death_events.count = src->death_events.count;
    dst->death_events.next_id = src->death_events.next_id;
    for (i = 0u; i < src->death_events.count; ++i) {
        dst->death_events.events[i] = src->death_events.events[i];
    }
    dst->estates.count = src->estates.count;
    dst->estates.next_id = src->estates.next_id;
    dst->estates.account_used = src->estates.account_used;
    for (i = 0u; i < src->estates.count; ++i) {
        dst->estates.estates[i] = src->estates.estates[i];
    }
    for (i = 0u; i < src->estates.account_used; ++i) {
        dst->estates.account_storage[i] = src->estates.account_storage[i];
    }
    dst->bindings.count = src->bindings.count;
    for (i = 0u; i < src->bindings.count; ++i) {
        dst->bindings.bindings[i] = src->bindings.bindings[i];
    }
    dst->ledger = src->ledger;
}
