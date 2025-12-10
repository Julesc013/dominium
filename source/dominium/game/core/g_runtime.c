#include "g_runtime.h"
#include <string.h>

static DmnGameLaunchOptions g_launch_opts = {
    DMN_GAME_MODE_GUI,
    DMN_GAME_SERVER_OFF,
    0
};

void dmn_game_default_options(DmnGameLaunchOptions* out)
{
    if (!out) return;
    *out = g_launch_opts;
}

void dmn_game_set_launch_options(const DmnGameLaunchOptions* opts)
{
    if (!opts) return;
    g_launch_opts = *opts;
}

const DmnGameLaunchOptions* dmn_game_get_launch_options(void)
{
    return &g_launch_opts;
}
