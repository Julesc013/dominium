/*
FILE: source/domino/render/herc/herc_hw.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/herc/herc_hw
RESPONSIBILITY: Implements `herc_hw`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_HERC_HW_H
#define DOMINIUM_HERC_HW_H

#include <stdint.h>

#include "herc_gfx.h"

/* Initialize Hercules subsystem if needed. */
int herc_hw_init(void);

/* Set Hercules 720x348 1bpp graphics mode.
   Implement via BIOS or direct register pokes; return 0 on success. */
int herc_hw_set_mode_720x348(herc_mode_info* out_mode);

/* Restore text mode (e.g. 80x25). */
void herc_hw_restore_text_mode(void);

/* Blit 8bpp or 1bpp system RAM framebuffer to Hercules VRAM.
   src: system RAM buffer; in v1, treat as 8bpp grayscale or indexed.
   Implementation must:
       - Threshold or map src values to on/off (1bpp)
       - Pack bits into bytes according to Hercules layout
       - Store to VRAM starting at 0xB000:0000
*/
void herc_hw_blit_720x348(const uint8_t* src,
                          uint16_t width,
                          uint16_t height,
                          uint16_t src_stride);

#endif /* DOMINIUM_HERC_HW_H */
