#include "domino/app/startup.h"
#include "dom_game_app.h"

#include <cstdio>

namespace {

static int run_game_with_config(dom::GameConfig &cfg) {
    dom::DomGameApp app;
    if (!app.init_from_cli(cfg)) {
        return 1;
    }
    app.run();
    app.shutdown();
    return 0;
}

static int run_game_with_mode(const d_app_params *p, dom::GameMode mode) {
    dom::GameConfig cfg;
    dom::init_default_game_config(cfg);
    if (p) {
        if (!dom::parse_game_cli_args(p->argc, p->argv, cfg)) {
            return 1;
        }
    }
    cfg.mode = mode;
    return run_game_with_config(cfg);
}

} // namespace

extern "C" {

int dom_game_run_cli(const d_app_params* p) {
    dom::GameConfig cfg;
    dom::init_default_game_config(cfg);
    if (p) {
        if (!dom::parse_game_cli_args(p->argc, p->argv, cfg)) {
            return 1;
        }
    }
    return run_game_with_config(cfg);
}

int dom_game_run_tui(const d_app_params* p) {
    return run_game_with_mode(p, dom::GAME_MODE_TUI);
}

int dom_game_run_gui(const d_app_params* p) {
    return run_game_with_mode(p, dom::GAME_MODE_GUI);
}

int dom_game_run_headless(const d_app_params* p) {
    return run_game_with_mode(p, dom::GAME_MODE_HEADLESS);
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
