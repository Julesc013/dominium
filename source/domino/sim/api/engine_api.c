/*
FILE: source/domino/sim/api/engine_api.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/api/engine_api
RESPONSIBILITY: Implements `engine_api`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "engine_api.h"
#include <stdlib.h>
#include <string.h>

/* Stub engine implementation to satisfy foundation build. */

struct Engine {
    EngineConfig config;
};

Engine *engine_create(const EngineConfig *cfg)
{
    Engine *e = (Engine *)malloc(sizeof(Engine));
    if (!e) return NULL;
    if (cfg) {
        e->config = *cfg;
    } else {
        memset(&e->config, 0, sizeof(e->config));
    }
    return e;
}

void engine_destroy(Engine *engine)
{
    if (engine) free(engine);
}

b32 engine_load_universe(Engine *engine, const char *universe_path)
{
    (void)engine; (void)universe_path;
    return TRUE;
}

b32 engine_load_surface(Engine *engine, const char *universe_path, u32 surface_id)
{
    (void)engine; (void)universe_path; (void)surface_id;
    return TRUE;
}

b32 engine_save(Engine *engine, const char *universe_path)
{
    (void)engine; (void)universe_path;
    return TRUE;
}

void engine_tick(Engine *engine, fix32 dt)
{
    (void)engine; (void)dt;
}

void engine_get_services(Engine *engine, u32 surface_id, WorldServices *out)
{
    (void)engine; (void)surface_id; (void)out;
}
