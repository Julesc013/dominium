/*
FILE: source/domino/sim/_legacy/core_sim/sim_systems.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/sim_systems
RESPONSIBILITY: Implements `sim_systems`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SIM_SYSTEMS_H
#define DOM_SIM_SYSTEMS_H

#include "core_fixed.h"
#include "sim_world.h"
#include "world_surface.h"

void sim_tick_surface(SurfaceRuntime *surface, WorldServices *ws, fix32 dt);

#endif /* DOM_SIM_SYSTEMS_H */
