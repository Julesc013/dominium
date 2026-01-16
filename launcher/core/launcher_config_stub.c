/*
Stub launcher config persistence.
*/
#include "launcher/launcher_config.h"

#include <string.h>

int launcher_config_load(launcher_config* cfg)
{
    if (!cfg) {
        return -1;
    }
    memset(cfg, 0, sizeof(*cfg));
    return -1;
}

int launcher_config_save(const launcher_config* cfg)
{
    (void)cfg;
    return -1;
}
