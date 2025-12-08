#include "runtime_display.h"
#include "runtime_app.h"

#include <cstdio>

int run_game_headless(const RuntimeConfig &cfg)
{
    std::printf("dom_main headless role=%s universe=%s display=none\n",
                cfg.role.c_str(),
                cfg.universe_path.c_str());
    return 0;
}
