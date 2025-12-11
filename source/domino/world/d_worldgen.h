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
