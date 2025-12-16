/*
FILE: source/domino/sim/_legacy/core_sim/world_geom.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/world_geom
RESPONSIBILITY: Implements `world_geom`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_WORLD_GEOM_H
#define DOM_WORLD_GEOM_H

#include "core_fixed.h"
#include "registry_material.h"
#include "world_addr.h"

struct SurfaceRuntime;

typedef struct GeomSample {
    fix32 phi;
    MatId mat_id;
} GeomSample;

b32 geom_sample(struct SurfaceRuntime *surface, const SimPos *pos, GeomSample *out);

#endif /* DOM_WORLD_GEOM_H */
