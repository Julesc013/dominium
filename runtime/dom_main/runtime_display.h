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
