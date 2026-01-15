/*
FILE: source/domino/dmachine.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dmachine
RESPONSIBILITY: Implements `dmachine`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dmachine.h"
#include "domino/drecipe.h"

#include <string.h>

#define DMACHINE_MAX_TYPES 256
#define DMACHINE_MAX       2048
#define DMACHINE_FLAG_ENABLED  (1u << 0)

static MachineType g_types[DMACHINE_MAX_TYPES];
static Machine     g_machines[DMACHINE_MAX];
static bool        g_machine_used[DMACHINE_MAX];
static MachineTypeId g_type_count = 0;
static MachineId     g_machine_count = 0;

static PowerW dmachine_min_power(PowerW a, PowerW b)
{
    return (a < b) ? a : b;
}

MachineTypeId dmachine_type_register(const MachineType *def)
{
    MachineType copy;
    if (!def || !def->name) return 0;
    if (g_type_count >= (MachineTypeId)DMACHINE_MAX_TYPES) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (MachineTypeId)(g_type_count + 1);
    }
    g_types[g_type_count] = copy;
    g_type_count++;
    return copy.id;
}

const MachineType *dmachine_type_get(MachineTypeId id)
{
    if (id == 0 || id > g_type_count) return 0;
    return &g_types[id - 1];
}

MachineId dmachine_create(MachineTypeId type, AggregateId agg, ElementId element)
{
    U32 i;
    Machine *m = 0;
    if (type == 0) return 0;
    if (!dmachine_type_get(type)) return 0;
    for (i = 0; i < DMACHINE_MAX; ++i) {
        if (!g_machine_used[i]) {
            g_machine_used[i] = true;
            m = &g_machines[i];
            g_machine_count = (MachineId)((i + 1 > g_machine_count) ? (i + 1) : g_machine_count);
            break;
        }
    }
    if (!m) return 0;
    memset(m, 0, sizeof(*m));
    m->id = (MachineId)(i + 1);
    m->type_id = type;
    m->agg = agg;
    m->element = element;
    m->efficiency_0_1 = (Q16_16)(1 << 16);
    m->health_0_1 = (Q16_16)(1 << 16);
    m->flags = DMACHINE_FLAG_ENABLED;
    return m->id;
}

Machine *dmachine_get(MachineId id)
{
    if (id == 0 || id > g_machine_count) return 0;
    if (!g_machine_used[id - 1]) return 0;
    return &g_machines[id - 1];
}

void dmachine_destroy(MachineId id)
{
    if (id == 0 || id > g_machine_count) return;
    g_machine_used[id - 1] = false;
}

void dmachine_set_recipe(MachineId id, uint32_t recipe_id)
{
    Machine *m = dmachine_get(id);
    if (!m) return;
    m->recipe_id = recipe_id;
    m->progress_0_1 = 0;
}

void dmachine_set_enabled(MachineId id, bool enabled)
{
    Machine *m = dmachine_get(id);
    if (!m) return;
    if (enabled) {
        m->flags |= DMACHINE_FLAG_ENABLED;
    } else {
        m->flags &= ~DMACHINE_FLAG_ENABLED;
    }
}

void dmachine_tick(MachineId id, SimTick t)
{
    Machine *m = dmachine_get(id);
    const MachineType *type;
    const Recipe *rec = 0;
    RecipeStepResult step;
    (void)t;
    if (!m) return;
    type = dmachine_type_get(m->type_id);
    if (!type) return;
    m->power_draw_W = type->idle_power_W;
    m->power_output_W = 0;
    if ((m->flags & DMACHINE_FLAG_ENABLED) && m->recipe_id != 0) {
        rec = drecipe_get((RecipeId)m->recipe_id);
        if (rec) {
            m->power_draw_W = rec->power_in_W;
            m->power_output_W = rec->power_out_W;
            step = drecipe_step_machine(m, rec, t);
            if (step.batch_completed) {
                /* leave progress at 0; higher layer will move items/fluids */
            }
        }
    }
    m->power_draw_W = dmachine_min_power(m->power_draw_W, type->max_power_W);
}

void dmachine_tick_all(SimTick t)
{
    U32 i;
    for (i = 0; i < g_machine_count; ++i) {
        if (g_machine_used[i]) {
            dmachine_tick((MachineId)(i + 1), t);
        }
    }
}
