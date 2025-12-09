#ifndef DOMINIUM_EGA_HW_H
#define DOMINIUM_EGA_HW_H

#include <stdint.h>
#include "ega_gfx.h"

int ega_hw_init(void);

int ega_hw_set_mode_640x350_16(ega_mode_info* out_mode);

void ega_hw_restore_text_mode(void);

void ega_hw_blit_640x350_16(const uint8_t* src,
                            uint16_t width,
                            uint16_t height,
                            uint16_t src_stride);

#endif /* DOMINIUM_EGA_HW_H */
