/*
FILE: source/domino/render/vesa/vesa_bios.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/vesa/vesa_bios
RESPONSIBILITY: Implements `vesa_bios`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "vesa_bios.h"

/* Stub implementations; platform-specific VBE hooks can replace these. */

int vesa_bios_init(void)
{
    return -1;
}

int vesa_bios_find_mode(uint16_t req_w,
                        uint16_t req_h,
                        uint8_t req_bpp,
                        vesa_mode_info* out_mode)
{
    (void)req_w;
    (void)req_h;
    (void)req_bpp;
    (void)out_mode;
    return -1;
}

int vesa_bios_set_mode(const vesa_mode_info* mode, int use_linear)
{
    (void)mode;
    (void)use_linear;
    return -1;
}

void vesa_bios_restore_mode(void)
{
}

void* vesa_bios_map_lfb(const vesa_mode_info* mode)
{
    (void)mode;
    return (void*)0;
}

void vesa_bios_set_bank(uint16_t bank)
{
    (void)bank;
}
