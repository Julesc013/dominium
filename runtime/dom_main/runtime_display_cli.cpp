#include "runtime_display.h"
#include "runtime_app.h"

#include <cstdio>

int run_game_cli(const RuntimeConfig &cfg)
{
    std::printf("dom_main (CLI) role=%s universe=%s display=cli session=%s instance=%s\n",
                cfg.role.c_str(),
                cfg.universe_path.c_str(),
                cfg.launcher_session_id.c_str(),
                cfg.launcher_instance_id.c_str());
    return 0;
}
