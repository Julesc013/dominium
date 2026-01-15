/*
FILE: source/domino/render/ega/ega_hw.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/ega/ega_hw
RESPONSIBILITY: Defines internal contract for `ega_hw`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
