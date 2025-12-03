#include "dom_sim_world.h"
#include "dom_sim_ecs.h"
#include "dom_sim_events.h"
#include "dom_sim_jobs.h"
#include "dom_sim_time.h"
#include <stdlib.h>

struct DomSimWorld {
    DomSimConfig cfg;
};

dom_err_t dom_sim_world_create(const DomSimConfig *cfg, DomSimWorld **out_world)
{
    DomSimWorld *w;
    if (!cfg || !out_world) return DOM_ERR_INVALID_ARG;
    w = (DomSimWorld *)malloc(sizeof(DomSimWorld));
    if (!w) return DOM_ERR_OUT_OF_MEMORY;
    w->cfg = *cfg;

    dom_sim_tick_init(cfg);
    dom_sim_ecs_init();
    dom_sim_events_init();
    dom_sim_jobs_init();
    *out_world = w;
    return DOM_OK;
}

void dom_sim_world_destroy(DomSimWorld *world)
{
    if (!world) return;
    free(world);
}

dom_err_t dom_sim_world_step(DomSimWorld *world)
{
    (void)world;
    return dom_sim_tick_step();
}
