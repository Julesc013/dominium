#ifndef DOMINIUM_CGA_HW_H
#define DOMINIUM_CGA_HW_H

#include <stdint.h>
#include "cga_gfx.h"

int cga_hw_init(void);
int cga_hw_set_mode_320x200_4col(uint8_t palette, cga_mode_info* out_mode);
void cga_hw_restore_text_mode(void);

void cga_hw_blit_320x200_4col(const uint8_t* src,
                              uint16_t width,
                              uint16_t height,
                              uint16_t src_stride);

#endif /* DOMINIUM_CGA_HW_H */
