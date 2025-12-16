/*
FILE: source/domino/render/vga/vga_hw.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/vga/vga_hw
RESPONSIBILITY: Implements `vga_hw`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
