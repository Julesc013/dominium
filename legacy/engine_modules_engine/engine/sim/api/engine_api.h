/*
FILE: source/domino/sim/api/engine_api.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/api/engine_api
RESPONSIBILITY: Defines internal contract for `engine_api`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
