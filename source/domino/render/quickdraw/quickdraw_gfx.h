#ifndef DOMINIUM_QUICKDRAW_GFX_H
#define DOMINIUM_QUICKDRAW_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* Forward declarations from Mac OS headers; actual types defined in .c */
typedef struct WindowRecord* WindowPtr;
typedef struct CGrafPort*    CGrafPtr;
typedef struct GWorldRecord* GWorldPtr;

typedef struct quickdraw_state_t {
    void*     native_window;
    int       width;
    int       height;
    int       fullscreen;

    WindowPtr window;
    CGrafPtr  window_port;
    GWorldPtr offscreen_gworld;
    CGrafPtr  offscreen_port;

    int       depth;

    dgfx_caps caps;

    int       frame_in_progress;
} quickdraw_state_t;

extern quickdraw_state_t g_quickdraw;

const dgfx_backend_vtable* dgfx_quickdraw_get_vtable(void);

#endif /* DOMINIUM_QUICKDRAW_GFX_H */
