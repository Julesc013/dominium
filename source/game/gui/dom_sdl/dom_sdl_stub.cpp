#include <iostream>
#include <cstring>

extern "C" {
#include "dominium/dom_core.h"
}

static bool has_flag(int argc, char **argv, const char *flag)
{
    int i;
    for (i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], flag) == 0) return true;
    }
    return false;
}

static const char *engine_version_stub(void)
{
    return "0.0.0";
}

static void print_version_json(void)
{
    std::cout << "{\n";
    std::cout << "  \"schema_version\": 1,\n";
    std::cout << "  \"binary_id\": \"dom_sdl\",\n";
    std::cout << "  \"binary_version\": \"0.1.0\",\n";
    std::cout << "  \"engine_version\": \"" << engine_version_stub() << "\"\n";
    std::cout << "}\n";
}

static void print_capabilities_json(void)
{
    std::cout << "{\n";
    std::cout << "  \"schema_version\": 1,\n";
    std::cout << "  \"binary_id\": \"dom_sdl\",\n";
    std::cout << "  \"binary_version\": \"0.1.0\",\n";
    std::cout << "  \"engine_version\": \"" << engine_version_stub() << "\",\n";
    std::cout << "  \"roles\": [\"client\"],\n";
    std::cout << "  \"supported_display_modes\": [\"cli\", \"tui\", \"gui\"],\n";
    std::cout << "  \"supported_save_versions\": [1],\n";
    std::cout << "  \"supported_content_pack_versions\": [1]\n";
    std::cout << "}\n";
}

int main(int argc, char **argv)
{
    if (has_flag(argc, argv, "--version")) {
        print_version_json();
        return 0;
    }
    if (has_flag(argc, argv, "--capabilities")) {
        print_capabilities_json();
        return 0;
    }
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
