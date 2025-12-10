#include "runtime_display.h"
#include "runtime_app.h"

#include <cstdio>

int run_game_tui(const RuntimeConfig &cfg)
{
    std::printf("dom_main (TUI stub) role=%s universe=%s display=tui\n",
                cfg.role.c_str(),
                cfg.universe_path.c_str());
    return 0;
}
