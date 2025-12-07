#include "runtime_app.h"
#include "runtime_display.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#ifdef _WIN32
#include <io.h>
#else
#include <unistd.h>
#endif

extern "C" {
#include "dominium/dom_core.h"
#include "dom_core/dom_core_types.h"
#include "dom_core/dom_core_version.h"
}

#define DOM_MAIN_BINARY_ID "dom_main"
#define DOM_MAIN_BINARY_VERSION "0.1.0"

static bool is_tty()
{
#ifdef _WIN32
    return _isatty(_fileno(stdout)) != 0;
#else
    return isatty(fileno(stdout)) != 0;
#endif
}

int runtime_print_version()
{
    std::printf("{\n");
    std::printf("  \"schema_version\": 1,\n");
    std::printf("  \"binary_id\": \"%s\",\n", DOM_MAIN_BINARY_ID);
    std::printf("  \"binary_version\": \"%s\",\n", DOM_MAIN_BINARY_VERSION);
    std::printf("  \"engine_version\": \"%s\"\n", dom_version_full());
    std::printf("}\n");
    return 0;
}

int runtime_print_capabilities()
{
    std::printf("{\n");
    std::printf("  \"schema_version\": 1,\n");
    std::printf("  \"binary_id\": \"%s\",\n", DOM_MAIN_BINARY_ID);
    std::printf("  \"binary_version\": \"%s\",\n", DOM_MAIN_BINARY_VERSION);
    std::printf("  \"engine_version\": \"%s\",\n", dom_version_full());
    std::printf("  \"roles\": [\"client\", \"server\", \"tool\"],\n");
    std::printf("  \"supported_display_modes\": [\"none\", \"cli\", \"tui\", \"gui\"],\n");
    std::printf("  \"supported_save_versions\": [1],\n");
    std::printf("  \"supported_content_pack_versions\": [1]\n");
    std::printf("}\n");
    return 0;
}

int runtime_run(const RuntimeConfig &cfg)
{
    DomDisplayMode mode = parse_display_mode(cfg.display, is_tty());
    if (mode == DOM_DISPLAY_GUI) {
        return run_game_gui(cfg);
    } else if (mode == DOM_DISPLAY_TUI) {
        return run_game_tui(cfg);
    } else if (mode == DOM_DISPLAY_CLI) {
        return run_game_cli(cfg);
    }
    return run_game_headless(cfg);
}
