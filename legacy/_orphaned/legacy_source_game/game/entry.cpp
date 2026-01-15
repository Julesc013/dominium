/*
FILE: source/dominium/game/entry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/entry
RESPONSIBILITY: Implements `entry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/app/startup.h"
#include "dom_game_cli.h"
#include "dom_game_app.h"

#include <cstdio>

namespace {

static int run_game_with_mode(const d_app_params *p, dom_game_mode mode) {
    dom_game_config cfg;
    dom_game_cli_result res;

    dom_game_cli_init_defaults(&cfg);
    dom_game_cli_init_result(&res);

    if (p && dom_game_cli_parse(p->argc, p->argv, &cfg, &res) != 0) {
        if (res.error[0]) {
            std::fprintf(stderr, "Error: %s\n", res.error);
        }
        return res.exit_code ? res.exit_code : 2;
    }

    if (res.want_help) {
        dom_game_cli_print_help(stdout);
        return 0;
    }
    if (res.want_version) {
        return dom_game_cli_print_version(stdout);
    }
    if (res.want_capabilities) {
        return dom_game_cli_print_capabilities(stdout);
    }
    if (res.want_introspect_json) {
        return dom_game_cli_print_introspect_json(stdout);
    }
    if (res.want_print_caps) {
        return dom_game_cli_print_caps(stdout);
    }
    if (res.want_print_selection) {
        const int rc = dom_game_cli_print_selection(&cfg.profile, stdout, stderr);
        return (rc == 0) ? 0 : 2;
    }
    if (res.want_smoke_gui) {
        return dom_game_cli_dispatch(p ? p->argc : 0, p ? p->argv : (char **)0);
    }

    cfg.mode = mode;
    return dom_game_run_config(&cfg);
}

} // namespace

extern "C" {

int dom_game_run_cli(const d_app_params* p) {
    if (!p) {
        return 1;
    }
    return dom_game_cli_dispatch(p->argc, p->argv);
}

int dom_game_run_tui(const d_app_params* p) {
    return run_game_with_mode(p, DOM_GAME_MODE_TUI);
}

int dom_game_run_gui(const d_app_params* p) {
    return run_game_with_mode(p, DOM_GAME_MODE_GUI);
}

int dom_game_run_headless(const d_app_params* p) {
    return run_game_with_mode(p, DOM_GAME_MODE_HEADLESS);
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
