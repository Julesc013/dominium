/*
FILE: source/domino/app/startup.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / app/startup
RESPONSIBILITY: Implements `startup`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/app/startup.h"

#include <string.h>

/* These will be defined in C++ on the Dominium side; declare as C functions. */
int dom_launcher_run_cli(const d_app_params* p);
int dom_launcher_run_tui(const d_app_params* p);
int dom_launcher_run_gui(const d_app_params* p);

int dom_game_run_cli(const d_app_params* p);
int dom_game_run_tui(const d_app_params* p);
int dom_game_run_gui(const d_app_params* p);
int dom_game_run_headless(const d_app_params* p);

int dom_setup_run_cli(const d_app_params* p);
int dom_setup_run_tui(const d_app_params* p);
int dom_setup_run_gui(const d_app_params* p);

int dom_tools_run_cli(const d_app_params* p);
int dom_tools_run_tui(const d_app_params* p);
int dom_tools_run_gui(const d_app_params* p);

static int d_app_match_prefix(const char* arg, const char* prefix) {
    size_t len;
    if (!arg || !prefix) {
        return 0;
    }
    len = strlen(prefix);
    if (strncmp(arg, prefix, len) == 0) {
        return 1;
    }
    return 0;
}

static int d_app_match_flag(const char* arg, const char* flag) {
    if (!arg || !flag) {
        return 0;
    }
    if (strcmp(arg, flag) == 0) {
        return 1;
    }
    return 0;
}

d_app_mode d_app_parse_mode(int argc, char** argv) {
    int i;
    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) {
            continue;
        }
        if (d_app_match_prefix(arg, "--mode=cli")) {
            return D_APP_MODE_CLI;
        }
        if (d_app_match_prefix(arg, "--mode=tui")) {
            return D_APP_MODE_TUI;
        }
        if (d_app_match_prefix(arg, "--mode=gui")) {
            return D_APP_MODE_GUI;
        }
        if (d_app_match_prefix(arg, "--mode=headless")) {
            return D_APP_MODE_HEADLESS;
        }
    }
    return D_APP_MODE_AUTO;
}

int d_app_game_force_headless(int argc, char** argv) {
    int i;
    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) {
            continue;
        }
        if (d_app_match_prefix(arg, "--mode=headless") ||
            d_app_match_flag(arg, "--server") ||
            d_app_match_flag(arg, "--dedicated") ||
            d_app_match_flag(arg, "--listen")) {
            return 1;
        }
    }
    return 0;
}

d_app_capabilities d_app_caps_launcher(void) {
    d_app_capabilities caps;
    caps.has_cli = 1;
    caps.has_tui = 1;
    caps.has_gui = 1;
    caps.has_headless = 0;
    return caps;
}

d_app_capabilities d_app_caps_game(void) {
    d_app_capabilities caps;
    caps.has_cli = 1;
    caps.has_tui = 1;
    caps.has_gui = 1;
    caps.has_headless = 1;
    return caps;
}

d_app_capabilities d_app_caps_setup(void) {
    d_app_capabilities caps;
    caps.has_cli = 1;
    caps.has_tui = 1;
    caps.has_gui = 1;
    caps.has_headless = 0;
    return caps;
}

d_app_capabilities d_app_caps_tools(void) {
    d_app_capabilities caps;
    caps.has_cli = 1;
    caps.has_tui = 1;
    caps.has_gui = 1;
    caps.has_headless = 0;
    return caps;
}

int d_app_run_launcher(const d_app_params* p) {
    d_app_capabilities caps = d_app_caps_launcher();
    int rc;

    if (!p) {
        return 1;
    }

    switch (p->mode) {
    case D_APP_MODE_CLI:
        if (caps.has_cli) {
            return dom_launcher_run_cli(p);
        }
        return D_APP_ERR_NO_INTERFACE;
    case D_APP_MODE_TUI:
        if (caps.has_tui) {
            return dom_launcher_run_tui(p);
        }
        return D_APP_ERR_TUI_UNSUPPORTED;
    case D_APP_MODE_GUI:
        if (caps.has_gui) {
            return dom_launcher_run_gui(p);
        }
        return D_APP_ERR_GUI_UNSUPPORTED;
    case D_APP_MODE_HEADLESS:
        return D_APP_ERR_HEADLESS_ERROR;
    case D_APP_MODE_AUTO:
    default:
        break;
    }

    if (p->has_terminal) {
        if (caps.has_cli) {
            return dom_launcher_run_cli(p);
        }
        return D_APP_ERR_NO_INTERFACE;
    }

    if (caps.has_gui) {
        rc = dom_launcher_run_gui(p);
        if (rc != D_APP_ERR_GUI_UNSUPPORTED) {
            return rc;
        }
    }
    if (caps.has_tui) {
        rc = dom_launcher_run_tui(p);
        if (rc != D_APP_ERR_TUI_UNSUPPORTED) {
            return rc;
        }
    }
    if (caps.has_cli) {
        return dom_launcher_run_cli(p);
    }
    return D_APP_ERR_NO_INTERFACE;
}

int d_app_run_game(const d_app_params* p) {
    d_app_capabilities caps = d_app_caps_game();
    int rc;

    if (!p) {
        return 1;
    }

    if (d_app_game_force_headless(p->argc, p->argv)) {
        if (caps.has_headless) {
            return dom_game_run_headless(p);
        }
        return D_APP_ERR_HEADLESS_ERROR;
    }

    if (p->mode != D_APP_MODE_AUTO) {
        switch (p->mode) {
        case D_APP_MODE_CLI:
            if (caps.has_cli) {
                return dom_game_run_cli(p);
            }
            return D_APP_ERR_NO_INTERFACE;
        case D_APP_MODE_TUI:
            if (caps.has_tui) {
                return dom_game_run_tui(p);
            }
            return D_APP_ERR_TUI_UNSUPPORTED;
        case D_APP_MODE_GUI:
            if (caps.has_gui) {
                return dom_game_run_gui(p);
            }
            return D_APP_ERR_GUI_UNSUPPORTED;
        case D_APP_MODE_HEADLESS:
            if (caps.has_headless) {
                return dom_game_run_headless(p);
            }
            return D_APP_ERR_HEADLESS_ERROR;
        case D_APP_MODE_AUTO:
        default:
            break;
        }
    }

    if (p->has_terminal) {
        if (caps.has_cli) {
            return dom_game_run_cli(p);
        }
        if (caps.has_tui) {
            return dom_game_run_tui(p);
        }
        if (caps.has_gui) {
            return dom_game_run_gui(p);
        }
        return D_APP_ERR_NO_INTERFACE;
    }

    if (caps.has_gui) {
        rc = dom_game_run_gui(p);
        if (rc != D_APP_ERR_GUI_UNSUPPORTED) {
            return rc;
        }
    }
    if (caps.has_tui) {
        rc = dom_game_run_tui(p);
        if (rc != D_APP_ERR_TUI_UNSUPPORTED) {
            return rc;
        }
    }
    if (caps.has_cli) {
        return dom_game_run_cli(p);
    }
    return D_APP_ERR_NO_INTERFACE;
}

int d_app_run_setup(const d_app_params* p) {
    d_app_capabilities caps = d_app_caps_setup();
    int rc;

    if (!p) {
        return 1;
    }

    switch (p->mode) {
    case D_APP_MODE_CLI:
        if (caps.has_cli) {
            return dom_setup_run_cli(p);
        }
        return D_APP_ERR_NO_INTERFACE;
    case D_APP_MODE_TUI:
        if (caps.has_tui) {
            return dom_setup_run_tui(p);
        }
        return D_APP_ERR_TUI_UNSUPPORTED;
    case D_APP_MODE_GUI:
        if (caps.has_gui) {
            return dom_setup_run_gui(p);
        }
        return D_APP_ERR_GUI_UNSUPPORTED;
    case D_APP_MODE_HEADLESS:
        return D_APP_ERR_HEADLESS_ERROR;
    case D_APP_MODE_AUTO:
    default:
        break;
    }

    if (p->has_terminal) {
        if (caps.has_cli) {
            return dom_setup_run_cli(p);
        }
        return D_APP_ERR_NO_INTERFACE;
    }

    if (caps.has_gui) {
        rc = dom_setup_run_gui(p);
        if (rc != D_APP_ERR_GUI_UNSUPPORTED) {
            return rc;
        }
    }
    if (caps.has_tui) {
        rc = dom_setup_run_tui(p);
        if (rc != D_APP_ERR_TUI_UNSUPPORTED) {
            return rc;
        }
    }
    if (caps.has_cli) {
        return dom_setup_run_cli(p);
    }
    return D_APP_ERR_NO_INTERFACE;
}

int d_app_run_tools(const d_app_params* p) {
    d_app_capabilities caps = d_app_caps_tools();
    int rc;

    if (!p) {
        return 1;
    }

    switch (p->mode) {
    case D_APP_MODE_CLI:
        if (caps.has_cli) {
            return dom_tools_run_cli(p);
        }
        return D_APP_ERR_NO_INTERFACE;
    case D_APP_MODE_TUI:
        if (caps.has_tui) {
            return dom_tools_run_tui(p);
        }
        return D_APP_ERR_TUI_UNSUPPORTED;
    case D_APP_MODE_GUI:
        if (caps.has_gui) {
            return dom_tools_run_gui(p);
        }
        return D_APP_ERR_GUI_UNSUPPORTED;
    case D_APP_MODE_HEADLESS:
        return D_APP_ERR_HEADLESS_ERROR;
    case D_APP_MODE_AUTO:
    default:
        break;
    }

    if (p->has_terminal) {
        if (caps.has_cli) {
            return dom_tools_run_cli(p);
        }
        return D_APP_ERR_NO_INTERFACE;
    }

    if (caps.has_gui) {
        rc = dom_tools_run_gui(p);
        if (rc != D_APP_ERR_GUI_UNSUPPORTED) {
            return rc;
        }
    }
    if (caps.has_tui) {
        rc = dom_tools_run_tui(p);
        if (rc != D_APP_ERR_TUI_UNSUPPORTED) {
            return rc;
        }
    }
    if (caps.has_cli) {
        return dom_tools_run_cli(p);
    }
    return D_APP_ERR_NO_INTERFACE;
}
