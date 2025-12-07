#include <iostream>
#include <cstring>
#include <cstdlib>

extern "C" {
#include "dominium/dom_core.h"
}

typedef enum DomDisplayMode {
    DOM_DISPLAY_NONE = 0,
    DOM_DISPLAY_CLI  = 1,
    DOM_DISPLAY_TUI  = 2,
    DOM_DISPLAY_GUI  = 3
} DomDisplayMode;

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
    std::cout << "  \"binary_id\": \"dom_cli\",\n";
    std::cout << "  \"binary_version\": \"0.1.0\",\n";
    std::cout << "  \"engine_version\": \"" << engine_version_stub() << "\"\n";
    std::cout << "}\n";
}

static void print_capabilities_json(void)
{
    std::cout << "{\n";
    std::cout << "  \"schema_version\": 1,\n";
    std::cout << "  \"binary_id\": \"dom_cli\",\n";
    std::cout << "  \"binary_version\": \"0.1.0\",\n";
    std::cout << "  \"engine_version\": \"" << engine_version_stub() << "\",\n";
    std::cout << "  \"roles\": [\"client\", \"tool\"],\n";
    std::cout << "  \"supported_display_modes\": [\"none\", \"cli\", \"tui\", \"gui\"],\n";
    std::cout << "  \"supported_save_versions\": [1],\n";
    std::cout << "  \"supported_content_pack_versions\": [1]\n";
    std::cout << "}\n";
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
    const char *role_arg = get_arg_value(argc, argv, "--role");
    const char *display_arg = get_arg_value(argc, argv, "--display");
    const char *session_id = get_arg_value(argc, argv, "--launcher-session-id");
    const char *instance_id = get_arg_value(argc, argv, "--launcher-instance-id");
    const char *u_arg = get_arg_value(argc, argv, "--universe");
    (void)role_arg;
    (void)instance_id;

    if (has_flag(argc, argv, "--version")) {
        print_version_json();
        return 0;
    }
    if (has_flag(argc, argv, "--capabilities")) {
        print_capabilities_json();
        return 0;
    }

    DomDisplayMode display_mode = DOM_DISPLAY_GUI;
    if (display_arg) {
        if (std::strcmp(display_arg, "none") == 0) display_mode = DOM_DISPLAY_NONE;
        else if (std::strcmp(display_arg, "cli") == 0) display_mode = DOM_DISPLAY_CLI;
        else if (std::strcmp(display_arg, "tui") == 0) display_mode = DOM_DISPLAY_TUI;
        else if (std::strcmp(display_arg, "gui") == 0) display_mode = DOM_DISPLAY_GUI;
    }

    if (display_mode == DOM_DISPLAY_NONE) {
        std::cout << "dom_cli running in display=none";
        if (session_id) {
            std::cout << " (launcher session " << session_id << ")";
        }
        std::cout << "\n";
        return 0;
    }
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
