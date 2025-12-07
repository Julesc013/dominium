#ifndef DOM_SIM_SYSTEMS_H
#define DOM_SIM_SYSTEMS_H

#include "core_fixed.h"
#include "sim_world.h"
#include "world_surface.h"

void sim_tick_surface(SurfaceRuntime *surface, WorldServices *ws, fix32 dt);

#endif /* DOM_SIM_SYSTEMS_H */
