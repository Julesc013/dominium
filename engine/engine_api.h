#ifndef DOM_ENGINE_API_H
#define DOM_ENGINE_API_H

#include "core_fixed.h"
#include "sim_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct EngineConfig {
    u32 max_surfaces;
    u64 universe_seed;
} EngineConfig;

typedef struct Engine Engine;

Engine *engine_create(const EngineConfig *cfg);
void    engine_destroy(Engine *engine);

b32     engine_load_universe(Engine *engine, const char *universe_path);
b32     engine_load_surface(Engine *engine, const char *universe_path, u32 surface_id);
b32     engine_save(Engine *engine, const char *universe_path);

void    engine_tick(Engine *engine, fix32 dt);
void    engine_get_services(Engine *engine, u32 surface_id, WorldServices *out);

#ifdef __cplusplus
}
#endif

#endif /* DOM_ENGINE_API_H */
