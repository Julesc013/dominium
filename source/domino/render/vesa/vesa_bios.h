#ifndef DOMINIUM_VESA_BIOS_H
#define DOMINIUM_VESA_BIOS_H

#include <stdint.h>
#include "vesa_gfx.h"

/* Initialize VBE environment; query controller info if needed. */
int vesa_bios_init(void);

/* Choose a mode matching (width,height,bpp). Return 0 on success. */
int vesa_bios_find_mode(uint16_t req_w,
                        uint16_t req_h,
                        uint8_t req_bpp,
                        vesa_mode_info* out_mode);

/* Set the chosen VBE mode. If use_linear != 0 and supported, enable linear framebuffer. */
int vesa_bios_set_mode(const vesa_mode_info* mode, int use_linear);

/* Restore previous text mode / original graphics mode. */
void vesa_bios_restore_mode(void);

/* Map linear framebuffer into process address space (if possible). Returns pointer to VRAM or NULL. */
void* vesa_bios_map_lfb(const vesa_mode_info* mode);

/* For banked modes: set bank index. */
void vesa_bios_set_bank(uint16_t bank);

#endif /* DOMINIUM_VESA_BIOS_H */
