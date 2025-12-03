#ifndef DOM_SIM_WORLD_H
#define DOM_SIM_WORLD_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_core_id.h"
#include "dom_sim_tick.h"

typedef struct DomSimWorld DomSimWorld;

dom_err_t dom_sim_world_create(const DomSimConfig *cfg, DomSimWorld **out_world);
void      dom_sim_world_destroy(DomSimWorld *world);

dom_err_t dom_sim_world_step(DomSimWorld *world);

#endif /* DOM_SIM_WORLD_H */
