/* Deterministic simulation orchestrator (C89). */
#ifndef D_SIM_H
#define D_SIM_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_entity_id;

/* System IDs are just integers for now. */
typedef u16 d_system_id;

typedef struct d_sim_context {
    d_world *world;
    u32      tick_index;    /* global tick counter */
    q16_16   tick_duration; /* fixed dt per tick */
} d_sim_context;

/* Component registration remains subsystem-local; dsim only manages entities and systems. */

/* System vtable */
typedef struct dsim_system_vtable {
    d_system_id system_id;
    const char *name;

    /* Called once when sim is initialized. */
    void (*init)(d_sim_context *ctx);

    /*
     * Called every tick in deterministic order.
     * 'ticks' is how many fixed ticks to advance (usually 1; could be >1 for catchup).
     */
    void (*tick)(d_sim_context *ctx, u32 ticks);

    /* Optional: cleanup when sim shuts down. */
    void (*shutdown)(d_sim_context *ctx);
} dsim_system_vtable;

/* Initialize sim context for a world. */
int  d_sim_init(d_sim_context *ctx, d_world *world, q16_16 tick_duration);

/* Shutdown sim. */
void d_sim_shutdown(d_sim_context *ctx);

/* Register a system; must be called before d_sim_init or at engine startup. */
int  d_sim_register_system(const dsim_system_vtable *vt);

/* Run one or more ticks. */
int  d_sim_step(d_sim_context *ctx, u32 ticks);

#ifdef __cplusplus
}
#endif

#endif /* D_SIM_H */
