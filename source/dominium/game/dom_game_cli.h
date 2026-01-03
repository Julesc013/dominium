/*
FILE: source/dominium/game/dom_game_cli.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_cli
RESPONSIBILITY: Defines internal CLI contract for the game runtime; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: CLI-only contract (not ABI-stable).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_CLI_H
#define DOM_GAME_CLI_H

#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif
#include "domino/core/types.h"
#include "domino/profile.h"
#ifdef __cplusplus
} /* extern "C" */
#endif

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_GAME_PATH_MAX = 260,
    DOM_GAME_ID_MAX = 64,
    DOM_GAME_ADDR_MAX = 128,
    DOM_GAME_BACKEND_MAX = 32,
    DOM_GAME_ERROR_MAX = 256
};

typedef enum dom_game_mode {
    DOM_GAME_MODE_GUI = 0,
    DOM_GAME_MODE_TUI = 1,
    DOM_GAME_MODE_HEADLESS = 2
} dom_game_mode;

typedef enum dom_game_server_mode {
    DOM_GAME_SERVER_OFF = 0,
    DOM_GAME_SERVER_LISTEN = 1,
    DOM_GAME_SERVER_DEDICATED = 2
} dom_game_server_mode;

typedef struct dom_game_config {
    dom_game_mode        mode;
    dom_game_server_mode server_mode;
    u32                  net_port;
    u32                  tick_rate_hz;
    u32                  deterministic_test;
    u32                  dev_mode;
    u32                  demo_mode;
    u32                  replay_strict_content;
    u32                  dev_allow_ad_hoc_paths;

    char dominium_home[DOM_GAME_PATH_MAX];
    char instance_id[DOM_GAME_ID_MAX];
    char connect_addr[DOM_GAME_ADDR_MAX];
    char gfx_backend[DOM_GAME_BACKEND_MAX];
    char platform_backend[DOM_GAME_BACKEND_MAX];
    char replay_record_path[DOM_GAME_PATH_MAX];
    char replay_play_path[DOM_GAME_PATH_MAX];
    char save_path[DOM_GAME_PATH_MAX];
    char load_path[DOM_GAME_PATH_MAX];
    char handshake_path[DOM_GAME_PATH_MAX];

    dom_profile profile;
} dom_game_config;

typedef struct dom_game_cli_result {
    int want_help;
    int want_version;
    int want_capabilities;
    int want_print_caps;
    int want_print_selection;
    int want_introspect_json;
    int want_smoke_gui;
    int warned_renderer_alias;
    int exit_code;
    char error[DOM_GAME_ERROR_MAX];
} dom_game_cli_result;

void dom_game_cli_init_defaults(dom_game_config *out_cfg);
void dom_game_cli_init_result(dom_game_cli_result *out_result);
int  dom_game_cli_parse(int argc, char **argv, dom_game_config *out_cfg, dom_game_cli_result *out_result);

void dom_game_cli_print_help(FILE *out);
int  dom_game_cli_print_caps(FILE *out);
int  dom_game_cli_print_selection(const dom_profile *profile, FILE *out, FILE *err);
int  dom_game_cli_print_capabilities(FILE *out);
int  dom_game_cli_print_version(FILE *out);
int  dom_game_cli_print_introspect_json(FILE *out);

int dom_game_run_config(const dom_game_config *cfg);
int dom_game_cli_dispatch(int argc, char **argv);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_GAME_CLI_H */
