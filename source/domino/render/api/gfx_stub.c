/*
FILE: source/domino/render/api/gfx_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/gfx_stub
RESPONSIBILITY: Implements `gfx_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TODO: legacy renderer stub; superseded by domino_gfx_core/soft backend */
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
