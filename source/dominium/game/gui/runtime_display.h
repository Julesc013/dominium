/*
FILE: source/dominium/game/gui/runtime_display.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/gui/runtime_display
RESPONSIBILITY: Defines internal contract for `runtime_display`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
// Runtime display selection and dispatch for dom_main.
#ifndef DOM_MAIN_RUNTIME_DISPLAY_H
#define DOM_MAIN_RUNTIME_DISPLAY_H

#include <string>

enum DomDisplayMode {
    DOM_DISPLAY_NONE = 0,
    DOM_DISPLAY_CLI  = 1,
    DOM_DISPLAY_TUI  = 2,
    DOM_DISPLAY_GUI  = 3
};

struct RuntimeConfig;

DomDisplayMode parse_display_mode(const std::string &display, bool is_tty);

int run_game_cli(const RuntimeConfig &cfg);
int run_game_tui(const RuntimeConfig &cfg);
int run_game_gui(const RuntimeConfig &cfg);
int run_game_headless(const RuntimeConfig &cfg);

#endif /* DOM_MAIN_RUNTIME_DISPLAY_H */
