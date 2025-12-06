#include <iostream>

extern "C" {
#include "engine_api.h"
}

int main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    std::cout << "dom_sdl_stub: renderer/UI placeholder. Link check only.\n";
    EngineConfig cfg;
    Engine *engine;
    cfg.max_surfaces = 1;
    cfg.universe_seed = 1;
    engine = engine_create(&cfg);
    if (engine) {
        engine_destroy(engine);
    }
    return 0;
}
