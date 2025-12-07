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
