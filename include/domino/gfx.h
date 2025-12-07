#ifndef DOMINO_GFX_H
#define DOMINO_GFX_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dm_gfx_device dm_gfx_device;

struct dm_gfx_config {
    uint32_t width;
    uint32_t height;
    uint32_t flags;
};

struct dm_gfx_device {
    struct dm_gfx_config config;
    void*                impl;
};

dm_gfx_device* dm_gfx_create_device(const struct dm_gfx_config* cfg);
void           dm_gfx_destroy_device(dm_gfx_device* dev);
int            dm_gfx_begin_frame(dm_gfx_device* dev);
int            dm_gfx_end_frame(dm_gfx_device* dev);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_GFX_H */
