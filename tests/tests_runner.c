#include <stdio.h>

#include "engine_api.h"

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
