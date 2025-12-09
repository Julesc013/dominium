#ifndef DOMINIUM_QUARTZ_GFX_H
#define DOMINIUM_QUARTZ_GFX_H

#include <stdint.h>
#include <stddef.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* Forward declarations to avoid exposing macOS headers in public headers */
typedef struct CGContext* CGContextRef;
typedef struct CGColorSpace* CGColorSpaceRef;
typedef struct CGImage* CGImageRef;

/* quartz renderer state */
typedef struct quartz_state_t {
    dsys_window*  window;      /* dsys window provided in dgfx_desc */
    void*         ns_window;   /* native NSWindow* / NSView* handle */

    int           width;
    int           height;
    int           fullscreen;

    /* CoreGraphics objects */
    CGContextRef    bitmap_ctx;     /* CGBitmapContext we render into */
    CGColorSpaceRef color_space;    /* color space for the bitmap */
    void*           bitmap_data;    /* malloc'd pixel buffer backing the bitmap_ctx */
    size_t          bitmap_stride;  /* bytes per row */

    /* Optional: image wrapper for efficient blit */
    CGImageRef      bitmap_image;

    /* Format: ARGB/RGBA 8:8:8:8 premultiplied alpha */
    int             depth;          /* bits per pixel, e.g. 32 */

    dgfx_caps       caps;

    int             frame_in_progress;

    /* Simple 2D camera/viewport state */
    float           camera_offset_x;
    float           camera_offset_y;

} quartz_state_t;

extern quartz_state_t g_quartz;

const dgfx_backend_vtable* dgfx_quartz_get_vtable(void);

#endif /* DOMINIUM_QUARTZ_GFX_H */