/*
FILE: source/domino/render/cga/cga_hw.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/cga/cga_hw
RESPONSIBILITY: Implements `cga_hw`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
