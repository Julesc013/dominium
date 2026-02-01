/*
FILE: source/domino/env/d_env.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / env/d_env
RESPONSIBILITY: Defines internal contract for `d_env`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Environment subsystem types (C89). */
#ifndef D_ENV_H
#define D_ENV_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 denv_zone_id;

typedef struct denv_zone_state {
    denv_zone_id id;
    q16_16       temperature;
    q16_16       pressure;
    q16_16       humidity;
    q16_16       gas_mix[4];   /* simple vector; indices predefined elsewhere */
    q16_16       pollution;
    q16_16       light_level;
    d_tlv_blob   extra;        /* extra channels */
} denv_zone_state;

typedef struct denv_portal {
    denv_zone_id a;
    denv_zone_id b;
    q16_16       area;         /* m^2 */
    q16_16       permeability; /* 0..1 */
    d_tlv_blob   extra;
} denv_portal;

/* Initialize environment state for a chunk (zones, portals). */
int denv_init_chunk(d_world *w, d_chunk *chunk);

/* Tick environment models for a world or chunk. */
void denv_tick(d_world *w, u32 ticks);

/* Subsystem registration hook */
void d_env_init(void);
int d_env_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_ENV_H */
