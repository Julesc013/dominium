#ifndef DOMINIUM_LAUNCHER_APP_HPP
#define DOMINIUM_LAUNCHER_APP_HPP

#include "domino/core/types.h"

class LauncherApp {
public:
    LauncherApp();
    ~LauncherApp();

    int run(int argc, char** argv);
    int run_list_products();
    int run_run_game(u32 seed, u32 ticks, const char* instance_id);
    int run_run_tool(const char* tool_id);
    int run_manifest_info();
    int run_tui();
    int run_gui();
};

#endif /* DOMINIUM_LAUNCHER_APP_HPP */
