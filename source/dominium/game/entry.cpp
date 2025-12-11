#include "domino/app/startup.h"
#include "dominium/app/product_entry.hpp"
#include "dominium/game/game_app.hpp"

#include <cstdlib>
#include <cstring>

static void game_parse_headless_args(const d_app_params* p,
                                     u32* seed,
                                     u32* ticks,
                                     u32* width,
                                     u32* height) {
    int i;
    if (!p || !p->argv) {
        return;
    }
    for (i = 1; i < p->argc; ++i) {
        const char* arg = p->argv[i];
        if (!arg) continue;
        if (std::strncmp(arg, "--seed=", 7) == 0) {
            *seed = (u32)std::strtoul(arg + 7, NULL, 10);
        } else if (std::strncmp(arg, "--ticks=", 8) == 0) {
            *ticks = (u32)std::strtoul(arg + 8, NULL, 10);
        } else if (std::strncmp(arg, "--width=", 8) == 0) {
            *width = (u32)std::strtoul(arg + 8, NULL, 10);
        } else if (std::strncmp(arg, "--height=", 9) == 0) {
            *height = (u32)std::strtoul(arg + 9, NULL, 10);
        }
    }
}

extern "C" {

int dom_game_run_cli(const d_app_params* p) {
    GameApp app;
    if (!p) {
        return 1;
    }
    return app.run(p->argc, p->argv);
}

int dom_game_run_tui(const d_app_params* p) {
    GameApp app;
    (void)p;
    return app.run_tui_mode();
}

int dom_game_run_gui(const d_app_params* p) {
    GameApp app;
    (void)p;
    return app.run_gui_mode();
}

int dom_game_run_headless(const d_app_params* p) {
    u32 seed = 12345u;
    u32 ticks = 100u;
    u32 width = 64u;
    u32 height = 64u;
    GameApp app;
    game_parse_headless_args(p, &seed, &ticks, &width, &height);
    return app.run_headless(seed, ticks, width, height);
}

int dom_launcher_run_cli(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_NO_INTERFACE;
}

int dom_launcher_run_tui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_TUI_UNSUPPORTED;
}

int dom_launcher_run_gui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_GUI_UNSUPPORTED;
}

int dom_setup_run_cli(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_NO_INTERFACE;
}

int dom_setup_run_tui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_TUI_UNSUPPORTED;
}

int dom_setup_run_gui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_GUI_UNSUPPORTED;
}

int dom_tools_run_cli(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_NO_INTERFACE;
}

int dom_tools_run_tui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_TUI_UNSUPPORTED;
}

int dom_tools_run_gui(const d_app_params* p) {
    (void)p;
    return D_APP_ERR_GUI_UNSUPPORTED;
}

} /* extern "C" */
