#ifndef DOMINIUM_XGA_HW_H
#define DOMINIUM_XGA_HW_H

#include <stdint.h>
#include "xga_gfx.h"

/* Initialize XGA subsystem; detect framebuffer capabilities if needed. */
int xga_hw_init(void);

/* Choose and set an XGA graphics mode (e.g. 640x480x8).
   The implementation may ignore requested w/h and pick the closest supported.
   Return 0 on success and fill out_mode. */
int xga_hw_set_mode(uint16_t req_w, uint16_t req_h, xga_mode_info *out_mode);

/* Restore previous text/graphics mode. */
void xga_hw_restore_mode(void);

/* Blit full framebuffer from system RAM (8bpp indexed) to XGA VRAM. */
void xga_hw_blit(const uint8_t *src,
                 uint16_t width,
                 uint16_t height,
                 uint16_t src_stride,
                 const xga_mode_info *mode);

#endif /* DOMINIUM_XGA_HW_H */
