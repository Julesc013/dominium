/*
FILE: game/rules/infrastructure/machine_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / infrastructure
RESPONSIBILITY: Implements event-driven machine scheduler for production.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduling and processing are deterministic.
*/
#include "dominium/rules/infrastructure/machine_scheduler.h"

#include <string.h>

void machine_scheduler_params_default(machine_scheduler_params* params)
{
    if (!params) {
        return;
    }
    params->retry_interval = 5u;
    params->cooldown_interval = 0u;
    params->maintenance_degrade = 1u;
    params->maintenance_min_operational = 20u;
}

static int machine_has_inputs(const building_machine* machine,
                              const production_recipe* recipe,
                              const infra_store_registry* stores)
{
    u32 i;
    if (!machine || !recipe || !stores) {
        return 0;
    }
    for (i = 0u; i < recipe->input_count; ++i) {
        u32 needed = recipe->inputs[i].qty;
        u32 available = 0u;
        u32 s;
        for (s = 0u; s < machine->input_store_count; ++s) {
            u32 qty = 0u;
            (void)infra_store_get_qty(stores, machine->input_stores[s],
                                      recipe->inputs[i].asset_id, &qty);
            available += qty;
            if (available >= needed) {
                break;
            }
        }
        if (available < needed) {
            return 0;
        }
    }
    return 1;
}

static int machine_consume_inputs(const building_machine* machine,
                                  const production_recipe* recipe,
                                  infra_store_registry* stores)
{
    u32 i;
    if (!machine || !recipe || !stores) {
        return -1;
    }
    for (i = 0u; i < recipe->input_count; ++i) {
        u32 remaining = recipe->inputs[i].qty;
        u32 s;
        for (s = 0u; s < machine->input_store_count && remaining > 0u; ++s) {
            u32 taken = 0u;
            (void)infra_store_take(stores,
                                   machine->input_stores[s],
                                   recipe->inputs[i].asset_id,
                                   remaining,
                                   &taken);
            if (taken > remaining) {
                taken = remaining;
            }
            remaining -= taken;
        }
        if (remaining > 0u) {
            return -2;
        }
    }
    return 0;
}

static int machine_produce_outputs(const building_machine* machine,
                                   const production_recipe* recipe,
                                   infra_store_registry* stores)
{
    u32 i;
    if (!machine || !recipe || !stores) {
        return -1;
    }
    if (machine->output_store_count == 0u) {
        return -2;
    }
    for (i = 0u; i < recipe->output_count; ++i) {
        (void)infra_store_add(stores,
                              machine->output_stores[0],
                              recipe->outputs[i].asset_id,
                              recipe->outputs[i].qty);
    }
    return 0;
}

static dom_act_time_t machine_due_next_tick(void* user, dom_act_time_t now_tick)
{
    machine_due_user* due = (machine_due_user*)user;
    (void)now_tick;
    if (!due || !due->machine) {
        return DG_DUE_TICK_NONE;
    }
    return due->machine->next_due_tick;
}

static int machine_due_process_until(void* user, dom_act_time_t target_tick)
{
    machine_due_user* due = (machine_due_user*)user;
    machine_scheduler* sched;
    building_machine* machine;
    const production_recipe* recipe;
    dom_act_time_t next_tick;
    civ1_refusal_code refusal = CIV1_REFUSAL_NONE;

    if (!due || !due->scheduler || !due->machine) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    machine = due->machine;
    next_tick = machine->next_due_tick;
    if (next_tick == DG_DUE_TICK_NONE || next_tick > target_tick) {
        return DG_DUE_OK;
    }

    while (next_tick != DG_DUE_TICK_NONE && next_tick <= target_tick) {
        sched->processed_last += 1u;
        sched->processed_total += 1u;
        recipe = production_recipe_find(sched->recipes, machine->production_recipe_ref);
        if (!recipe) {
            machine->next_due_tick = DG_DUE_TICK_NONE;
            return DG_DUE_OK;
        }
        if (machine->status == MACHINE_PRODUCING) {
            if (machine->production_end_tick <= next_tick) {
                (void)machine_produce_outputs(machine, recipe, sched->stores);
                maintenance_degrade(&machine->maintenance, sched->params.maintenance_degrade);
                if (!maintenance_is_operational(&machine->maintenance) ||
                    machine->maintenance.level < sched->params.maintenance_min_operational) {
                    machine->status = MACHINE_HALTED;
                    refusal = CIV1_REFUSAL_MAINTENANCE_TOO_LOW;
                    machine->next_due_tick = next_tick + sched->params.retry_interval;
                } else {
                    machine->status = MACHINE_IDLE;
                    machine->next_due_tick = next_tick + sched->params.cooldown_interval;
                }
                machine->production_end_tick = DG_DUE_TICK_NONE;
            } else {
                machine->next_due_tick = machine->production_end_tick;
            }
        } else {
            if (!maintenance_is_operational(&machine->maintenance) ||
                machine->maintenance.level < sched->params.maintenance_min_operational) {
                machine->status = MACHINE_HALTED;
                refusal = CIV1_REFUSAL_MAINTENANCE_TOO_LOW;
                machine->next_due_tick = next_tick + sched->params.retry_interval;
            } else if (!machine_has_inputs(machine, recipe, sched->stores)) {
                refusal = CIV1_REFUSAL_INSUFFICIENT_INPUTS;
                machine->status = MACHINE_IDLE;
                machine->next_due_tick = next_tick + sched->params.retry_interval;
            } else {
                if (machine_consume_inputs(machine, recipe, sched->stores) != 0) {
                    refusal = CIV1_REFUSAL_INSUFFICIENT_INPUTS;
                    machine->status = MACHINE_IDLE;
                    machine->next_due_tick = next_tick + sched->params.retry_interval;
                } else {
                    machine->status = MACHINE_PRODUCING;
                    machine->production_end_tick = next_tick + recipe->duration_act;
                    machine->next_due_tick = machine->production_end_tick;
                }
            }
        }
        next_tick = machine->next_due_tick;
    }
    (void)refusal;
    return DG_DUE_OK;
}

static dg_due_vtable g_machine_due_vtable = {
    machine_due_next_tick,
    machine_due_process_until
};

int machine_scheduler_init(machine_scheduler* sched,
                           dom_time_event* event_storage,
                           u32 event_capacity,
                           dg_due_entry* entry_storage,
                           machine_due_user* user_storage,
                           u32 entry_capacity,
                           dom_act_time_t start_tick,
                           building_machine_registry* machines,
                           const production_recipe_registry* recipes,
                           infra_store_registry* stores,
                           const machine_scheduler_params* params)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !machines || !recipes || !stores) {
        return -1;
    }
    rc = dg_due_scheduler_init(&sched->due,
                               event_storage,
                               event_capacity,
                               entry_storage,
                               entry_capacity,
                               start_tick);
    if (rc != DG_DUE_OK) {
        return -2;
    }
    sched->due_events = event_storage;
    sched->due_entries = entry_storage;
    sched->due_users = user_storage;
    sched->machines = machines;
    sched->recipes = recipes;
    sched->stores = stores;
    if (params) {
        sched->params = *params;
    } else {
        machine_scheduler_params_default(&sched->params);
    }
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(machine_due_user) * (size_t)entry_capacity);
    return 0;
}

static int machine_scheduler_alloc_handle(machine_scheduler* sched, u32* out_handle)
{
    u32 i;
    if (!sched || !sched->due.entries || !out_handle) {
        return -1;
    }
    for (i = 0u; i < sched->due.entry_capacity; ++i) {
        if (!sched->due.entries[i].in_use) {
            *out_handle = i;
            return 0;
        }
    }
    return -2;
}

int machine_scheduler_register(machine_scheduler* sched,
                               building_machine* machine)
{
    u32 handle;
    machine_due_user* due;
    if (!sched || !machine) {
        return -1;
    }
    if (machine_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    if (machine->next_due_tick == DOM_TIME_ACT_MAX) {
        machine->next_due_tick = sched->due.current_tick;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->machine = machine;
    if (dg_due_scheduler_register(&sched->due, &g_machine_due_vtable, due,
                                  machine->building_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int machine_scheduler_advance(machine_scheduler* sched,
                              dom_act_time_t target_tick,
                              civ1_refusal_code* out_refusal)
{
    if (out_refusal) {
        *out_refusal = CIV1_REFUSAL_NONE;
    }
    if (!sched) {
        return -1;
    }
    sched->processed_last = 0u;
    if (dg_due_scheduler_advance(&sched->due, target_tick) != DG_DUE_OK) {
        if (out_refusal) {
            *out_refusal = CIV1_REFUSAL_INSUFFICIENT_INPUTS;
        }
        return -2;
    }
    return 0;
}

dom_act_time_t machine_scheduler_next_due(const machine_scheduler* sched)
{
    dom_time_event ev;
    if (!sched) {
        return DG_DUE_TICK_NONE;
    }
    if (dom_time_event_peek(&sched->due.queue, &ev) != DOM_TIME_OK) {
        return DG_DUE_TICK_NONE;
    }
    return ev.trigger_time;
}
