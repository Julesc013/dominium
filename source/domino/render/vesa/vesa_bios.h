/*
FILE: source/domino/render/vesa/vesa_bios.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/vesa/vesa_bios
RESPONSIBILITY: Defines internal contract for `vesa_bios`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
