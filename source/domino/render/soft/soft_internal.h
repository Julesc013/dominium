#ifndef DOMINO_SOFT_INTERNAL_H
#define DOMINO_SOFT_INTERNAL_H

#include "domino/gfx.h"

typedef struct domino_soft_target_ops {
    const char* name;
    int  (*init)(domino_sys_context* sys, int width, int height, domino_pixfmt fmt, void** out_state);
    void (*shutdown)(void* state);
    int  (*present)(void* state, const void* pixels, int width, int height, int stride_bytes);
} domino_soft_target_ops;

const domino_soft_target_ops* domino_soft_target_win32(void);
const domino_soft_target_ops* domino_soft_target_null(void);

int  domino_gfx_soft_create(domino_sys_context* sys,
                            const domino_gfx_desc* desc,
                            domino_gfx_device** out_dev);

#endif /* DOMINO_SOFT_INTERNAL_H */
