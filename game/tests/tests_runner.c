/*
FILE: tests/tests_runner.c
MODULE: Repository
LAYER / SUBSYSTEM: tests
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "dominium/dom_core.h"

int main(void)
{
    EngineConfig cfg;
    Engine *engine;
    cfg.max_surfaces = 1;
    cfg.universe_seed = 1234;

    engine = engine_create(&cfg);
    if (!engine) {
        printf("engine_create failed\n");
        return 1;
    }

    if (!engine_load_universe(engine, "saves/test")) {
        printf("engine_load_universe failed\n");
        engine_destroy(engine);
        return 1;
    }
    engine_tick(engine, FIX32_ONE);
    engine_save(engine, "saves/test");
    engine_destroy(engine);
    printf("dom_tests smoke passed\n");
    return 0;
}
