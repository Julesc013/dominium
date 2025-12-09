#ifndef DOMINIUM_MDA_HW_H
#define DOMINIUM_MDA_HW_H

#include <stdint.h>
#include "mda_gfx.h"

/* Initialize MDA hardware (stub OK) */
int mda_hw_init(void);

/* Switch to 720x350 1bpp MDA graphics mode */
int mda_hw_set_mode_720x350(mda_mode_info *out_mode);

/* Restore text mode (80x25) */
void mda_hw_restore_text_mode(void);

/* Copy 8bpp system RAM framebuffer into MDA VRAM:
   - threshold src pixels to 1-bit (on/off)
   - pack 8 pixels into 1 byte
   - apply MDA memory layout (interlaced row addressing)
*/
void mda_hw_blit_720x350(const uint8_t *src,
                         uint16_t width,
                         uint16_t height,
                         uint16_t stride_bytes);

#endif
