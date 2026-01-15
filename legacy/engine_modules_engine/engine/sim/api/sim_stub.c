/*
FILE: source/domino/sim/api/sim_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/api/sim_stub
RESPONSIBILITY: Implements `sim_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/sim.h"
#include <stdlib.h>

struct dm_sim_context {
    struct dm_sim_config cfg;
};

dm_sim_context* dm_sim_create(const struct dm_sim_config* cfg)
{
    dm_sim_context* sim = (dm_sim_context*)malloc(sizeof(dm_sim_context));
    if (!sim) return NULL;
    if (cfg) sim->cfg = *cfg;
    else sim->cfg.seed = 0;
    return sim;
}

void dm_sim_destroy(dm_sim_context* sim)
{
    if (sim) free(sim);
}

void dm_sim_tick(dm_sim_context* sim, uint32_t dt_usec)
{
    (void)sim;
    (void)dt_usec;
}
