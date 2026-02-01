/*
FILE: source/domino/world/d_worldgen.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/d_worldgen
RESPONSIBILITY: Defines internal contract for `d_worldgen`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* World generation provider registry (C89). */
#ifndef D_WORLDGEN_H
#define D_WORLDGEN_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

struct d_world;
struct d_chunk;

typedef u16 d_worldgen_provider_id;

typedef struct d_worldgen_provider {
    d_worldgen_provider_id id;
    const char            *name;

    /* Null-terminated list of provider_ids this provider depends on. */
    const d_worldgen_provider_id *depends_on;

    /* Called per chunk when it is first generated. */
    void (*populate_chunk)(
        struct d_world *w,
        struct d_chunk *chunk
    );
} d_worldgen_provider;

/* Register a worldgen provider; returns 0 on success. */
int  d_worldgen_register(const d_worldgen_provider *prov);

/* Called by d_world_generate_chunk to run providers in dependency order. */
int  d_worldgen_run(
    struct d_world *w,
    struct d_chunk *chunk
);

#ifdef __cplusplus
}
#endif

#endif /* D_WORLDGEN_H */
