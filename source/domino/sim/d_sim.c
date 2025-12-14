#include <stdio.h>

#include "d_sim.h"
#include "core/d_subsystem.h"
#include "net/d_net_apply.h"

#define DSIM_MAX_SYSTEMS 64u

static dsim_system_vtable g_dsim_systems[DSIM_MAX_SYSTEMS];
static u32 g_dsim_system_count = 0u;

int d_sim_register_system(const dsim_system_vtable *vt) {
    u32 i;
    if (!vt) {
        fprintf(stderr, "d_sim_register_system: NULL vtable\n");
        return -1;
    }
    if (vt->system_id == 0u) {
        fprintf(stderr, "d_sim_register_system: invalid id 0\n");
        return -2;
    }
    for (i = 0u; i < g_dsim_system_count; ++i) {
        if (g_dsim_systems[i].system_id == vt->system_id) {
            fprintf(stderr, "d_sim_register_system: duplicate id %u\n", (unsigned int)vt->system_id);
            return -3;
        }
    }
    if (g_dsim_system_count >= DSIM_MAX_SYSTEMS) {
        fprintf(stderr, "d_sim_register_system: registry full\n");
        return -4;
    }

    g_dsim_systems[g_dsim_system_count] = *vt;
    g_dsim_system_count += 1u;
    return 0;
}

int d_sim_init(d_sim_context *ctx, d_world *world, q16_16 tick_duration) {
    u32 i;
    if (!ctx || !world) {
        return -1;
    }

    ctx->world = world;
    ctx->tick_index = 0u;
    ctx->tick_duration = tick_duration;

    /* Deterministic: systems initialized in registration order. */
    for (i = 0u; i < g_dsim_system_count; ++i) {
        if (g_dsim_systems[i].init) {
            g_dsim_systems[i].init(ctx);
        }
    }
    return 0;
}

int d_sim_step(d_sim_context *ctx, u32 ticks) {
    u32 i;
    u32 t;
    if (!ctx || !ctx->world) {
        return -1;
    }

    for (t = 0u; t < ticks; ++t) {
        u32 subsystem_count;
        ctx->tick_index += 1u;
        ctx->world->tick_count += 1u;

        /* 0) Deterministic network command application for this tick. */
        (void)d_net_apply_for_tick(ctx->world, ctx->tick_index);

        /* 1) Global subsystem ticks (in registration order). */
        subsystem_count = d_subsystem_count();
        for (i = 0u; i < subsystem_count; ++i) {
            const d_subsystem_desc *desc = d_subsystem_get_by_index(i);
            if (desc && desc->tick) {
                desc->tick(ctx->world, 1u);
            }
        }

        /* 2) Local dsim systems. */
        for (i = 0u; i < g_dsim_system_count; ++i) {
            if (g_dsim_systems[i].tick) {
                g_dsim_systems[i].tick(ctx, 1u);
            }
        }
    }

    return 0;
}

void d_sim_shutdown(d_sim_context *ctx) {
    u32 i;
    if (!ctx) {
        return;
    }

    for (i = 0u; i < g_dsim_system_count; ++i) {
        if (g_dsim_systems[i].shutdown) {
            g_dsim_systems[i].shutdown(ctx);
        }
    }

    ctx->world = (d_world *)0;
    ctx->tick_index = 0u;
    ctx->tick_duration = 0;
}
