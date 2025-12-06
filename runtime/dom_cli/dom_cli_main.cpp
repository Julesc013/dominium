#include <iostream>
#include <cstring>
#include <cstdlib>

extern "C" {
#include "engine_api.h"
}

static const char *get_arg_value(int argc, char **argv, const char *key)
{
    int i;
    size_t key_len = std::strlen(key);
    for (i = 1; i < argc; ++i) {
        if (std::strncmp(argv[i], key, key_len) == 0) {
            const char *eq = argv[i] + key_len;
            if (*eq == '=' || *eq == ':') {
                return eq + 1;
            }
        }
    }
    return NULL;
}

int main(int argc, char **argv)
{
    const char *universe_path = "saves/default";
    const char *ticks_arg = NULL;
    const char *surface_arg = NULL;
    unsigned int surface_id = 0;
    unsigned int tick_count = 0;
    EngineConfig cfg;
    Engine *engine;
    fix32 dt = FIX32_ONE;
    const char *u_arg = get_arg_value(argc, argv, "--universe");
    if (u_arg) universe_path = u_arg;
    ticks_arg = get_arg_value(argc, argv, "--ticks");
    surface_arg = get_arg_value(argc, argv, "--surface");
    if (ticks_arg) {
        tick_count = (unsigned int)std::strtoul(ticks_arg, NULL, 10);
    } else {
        tick_count = 60;
    }
    if (surface_arg) {
        surface_id = (unsigned int)std::strtoul(surface_arg, NULL, 10);
    }

    cfg.max_surfaces = 4;
    cfg.universe_seed = 1;

    engine = engine_create(&cfg);
    if (!engine) {
        std::cerr << "Failed to create engine\n";
        return 1;
    }
    if (!engine_load_universe(engine, universe_path)) {
        std::cerr << "Failed to load universe at " << universe_path << "\n";
        engine_destroy(engine);
        return 1;
    }
    if (!engine_load_surface(engine, universe_path, surface_id)) {
        std::cerr << "Failed to load surface " << surface_id << "\n";
        engine_destroy(engine);
        return 1;
    }

    for (unsigned int i = 0; i < tick_count; ++i) {
        engine_tick(engine, dt);
    }

    if (!engine_save(engine, universe_path)) {
        std::cerr << "Failed to save universe\n";
        engine_destroy(engine);
        return 1;
    }
    engine_destroy(engine);
    std::cout << "Completed " << tick_count << " ticks for surface " << surface_id << " at " << universe_path << "\n";
    return 0;
}
