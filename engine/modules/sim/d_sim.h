/*
FILE: source/domino/sim/d_sim.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/d_sim
RESPONSIBILITY: Defines internal contract for `d_sim`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
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
