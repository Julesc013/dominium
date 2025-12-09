#ifndef DOMINIUM_VGA_HW_H
#define DOMINIUM_VGA_HW_H

#include <stdint.h>
#include "vga_gfx.h"

/* Initialize VGA hardware layer (stubbed on non-DOS builds). */
int vga_hw_init(void);

/* Enter mode 13h (320x200x8). Return 0 on success and fill mode info. */
int vga_hw_set_mode_13h(vga_mode_info *out_mode);

/* Restore previous text/graphics mode (stubbed). */
void vga_hw_restore_text_mode(void);

/* Optional direct pointer to VRAM (for flat/protected mode). */
uint8_t *vga_hw_get_vram_ptr(void);

/* Blit a full 320x200 (or smaller) framebuffer into VGA VRAM. */
void vga_hw_blit_13h(const uint8_t *src,
                     uint16_t width,
                     uint16_t height,
                     uint16_t src_stride);

#endif /* DOMINIUM_VGA_HW_H */
