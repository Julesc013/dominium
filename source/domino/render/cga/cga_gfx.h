#ifndef DOMINIUM_CGA_GFX_H
#define DOMINIUM_CGA_GFX_H

#include <stddef.h>
#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* Supported CGA graphics mode kind */
typedef enum cga_mode_kind_t {
    CGA_MODE_KIND_320x200_4COL = 0
} cga_mode_kind;

/* CGA mode info */
typedef struct cga_mode_info_t {
    cga_mode_kind kind;
    uint16_t      width;
    uint16_t      height;
    uint8_t       logical_bpp;
    uint8_t       palette;
    uint8_t       reserved[2];

    uint16_t      pitch_bytes;
    uint16_t      vram_segment;
} cga_mode_info;

typedef struct cga_state_t {
    cga_mode_info mode;

    /* System RAM framebuffer: 8bpp indexed */
    uint8_t* color;
    uint8_t* depth;
    uint8_t* stencil;

    int width;
    int height;
    int stride_bytes;

    int frame_in_progress;

    dgfx_caps caps;

    int camera_offset_x;
    int camera_offset_y;
} cga_state_t;

extern cga_state_t g_cga;

const dgfx_backend_vtable* dgfx_cga_get_vtable(void);

#endif /* DOMINIUM_CGA_GFX_H */
