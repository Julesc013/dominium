#include "domino/gfx.h"
#include <stdlib.h>

dm_gfx_device* dm_gfx_create_device(const struct dm_gfx_config* cfg)
{
    dm_gfx_device* dev = (dm_gfx_device*)malloc(sizeof(dm_gfx_device));
    if (!dev) return NULL;
    if (cfg) dev->config = *cfg;
    else {
        dev->config.width  = 0;
        dev->config.height = 0;
        dev->config.flags  = 0;
    }
    dev->impl = NULL;
    return dev;
}

void dm_gfx_destroy_device(dm_gfx_device* dev)
{
    if (dev) {
        free(dev);
    }
}

int dm_gfx_begin_frame(dm_gfx_device* dev)
{
    (void)dev;
    return 0;
}

int dm_gfx_end_frame(dm_gfx_device* dev)
{
    (void)dev;
    return 0;
}
