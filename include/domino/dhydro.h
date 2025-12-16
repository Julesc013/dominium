/*
FILE: include/domino/dhydro.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dhydro
RESPONSIBILITY: Defines the public contract for `dhydro` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DHYDRO_H
#define DOMINO_DHYDRO_H

#include "dnumeric.h"
#include "dworld.h"
#include "dfield.h"
#include "dorbit.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    BodyId   body;
    WPosTile from;
    WPosTile to;
    Q16_16   gradient; /* slope magnitude along the link */
} HydroRiverLink;

typedef struct {
    BodyId   body;
    WPosTile tile;
    Q16_16   outflow_u;
    Q16_16   outflow_v;
} HydroFlowSample;

FieldId dhydro_field_water_depth(void);

bool dhydro_init_body(BodyId body);
bool dhydro_register_river_link(const HydroRiverLink *link);

bool dhydro_step(BodyId body, ChunkPos region, U32 ticks);

bool dhydro_add_rainfall(BodyId body, const WPosTile *tile, Q16_16 water_depth);
bool dhydro_register_evaporation_bias(BodyId body, Q16_16 evap_per_tick);

bool dhydro_get_water_depth(BodyId body, const WPosTile *tile, Q16_16 *out_depth);
bool dhydro_get_flow(BodyId body, const WPosTile *tile, Q16_16 *out_flow_u, Q16_16 *out_flow_v);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DHYDRO_H */
