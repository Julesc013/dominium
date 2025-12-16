/*
FILE: source/domino/render/xga/xga_hw.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/xga/xga_hw
RESPONSIBILITY: Implements `xga_hw`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
