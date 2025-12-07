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
