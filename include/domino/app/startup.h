/*
FILE: include/domino/app/startup.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / app/startup
RESPONSIBILITY: Defines the public contract for `startup` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_APP_STARTUP_H
#define DOMINO_APP_STARTUP_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Startup modes shared across products. */
typedef enum d_app_mode {
    D_APP_MODE_AUTO = 0,
    D_APP_MODE_CLI,
    D_APP_MODE_TUI,
    D_APP_MODE_GUI,
    D_APP_MODE_HEADLESS  /* game only */
} d_app_mode;

/* Startup parameters passed from main() to dispatcher. */
typedef struct d_app_params {
    d_app_mode mode;       /* requested mode, or AUTO if none explicitly given */
    int        has_terminal;
    int        argc;
    char**     argv;
} d_app_params;

/* Capability mask per product. */
typedef struct d_app_capabilities {
    int has_cli;
    int has_tui;
    int has_gui;
    int has_headless; /* typically game only */
} d_app_capabilities;

/* Error codes for structural unsupported cases. */
#define D_APP_ERR_GUI_UNSUPPORTED   (-20)
#define D_APP_ERR_TUI_UNSUPPORTED   (-30)
#define D_APP_ERR_HEADLESS_ERROR    (-40)
#define D_APP_ERR_NO_INTERFACE      (64)

/* Parse explicit --mode=... flags from argv.
   Recognizes:
     --mode=cli
     --mode=tui
     --mode=gui
     --mode=headless    (game)
   Returns D_APP_MODE_AUTO if not present. */
d_app_mode d_app_parse_mode(int argc, char** argv);

/* Game-specific helper: detect if headless/server modes are forced. */
int d_app_game_force_headless(int argc, char** argv);

/* Product capability queries (to be implemented per-product or stubbed). */
d_app_capabilities d_app_caps_launcher(void);
d_app_capabilities d_app_caps_game(void);
d_app_capabilities d_app_caps_setup(void);
d_app_capabilities d_app_caps_tools(void);

/* Product dispatchers (implementation in startup.c calls C++ entrypoints). */
int d_app_run_launcher(const d_app_params* p);
int d_app_run_game(const d_app_params* p);
int d_app_run_setup(const d_app_params* p);
int d_app_run_tools(const d_app_params* p);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_APP_STARTUP_H */
