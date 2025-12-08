#include "domino/sim.h"

#include <stdlib.h>
#include <string.h>

struct dom_sim {
    dom_sim_desc desc;
    uint64_t     time_millis;
};

int dom_sim_create(const dom_sim_desc* desc, dom_sim** out_sim)
{
    dom_sim* sim;
    dom_sim_desc local_desc;

    if (!out_sim) {
        return -1;
    }
    *out_sim = NULL;

    sim = (dom_sim*)malloc(sizeof(dom_sim));
    if (!sim) {
        return -1;
    }
    memset(sim, 0, sizeof(*sim));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }

    local_desc.struct_size = sizeof(dom_sim_desc);
    sim->desc = local_desc;
    sim->time_millis = 0u;

    *out_sim = sim;
    return 0;
}

void dom_sim_destroy(dom_sim* sim)
{
    if (!sim) {
        return;
    }
    free(sim);
}

int dom_sim_tick(dom_sim* sim, uint32_t dt_millis)
{
    if (!sim) {
        return -1;
    }
    sim->time_millis += dt_millis;
    return 0;
}

int dom_sim_get_time(dom_sim* sim, uint64_t* out_time_millis)
{
    if (!sim || !out_time_millis) {
        return -1;
    }
    *out_time_millis = sim->time_millis;
    return 0;
}
