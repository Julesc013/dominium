/*
FILE: source/dominium/game/gui/dom_sdl/dom_sdl_stub.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/gui/dom_sdl/dom_sdl_stub
RESPONSIBILITY: Implements `dom_sdl_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
