/*
FILE: source/domino/render/vga/vga_hw.c
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
#include "vga_hw.h"

#include <string.h>

/* Stub VRAM buffer to mirror writes when real VGA hardware is unavailable. */
static uint8_t g_vga_vram[320u * 200u];
static uint16_t g_vga_pitch = 320u;
static uint16_t g_vga_height = 200u;

int vga_hw_init(void)
{
    /* Stub always succeeds; real implementation would probe VGA hardware. */
    return 0;
}

int vga_hw_set_mode_13h(vga_mode_info *out_mode)
{
    vga_mode_info mode;

    memset(&mode, 0, sizeof(mode));
    mode.kind = VGA_MODE_KIND_13H;
    mode.width = 320u;
    mode.height = 200u;
    mode.bpp = 8u;
    mode.vram_phys = 0xA0000u;
    mode.vram_segment = 0xA000u;
    mode.pitch_bytes = 320u;

    if (out_mode) {
        *out_mode = mode;
    }

    g_vga_pitch = mode.pitch_bytes;
    g_vga_height = mode.height;

    return 0;
}

void vga_hw_restore_text_mode(void)
{
    /* Stub: a real implementation would restore INT 10h mode 3. */
}

uint8_t *vga_hw_get_vram_ptr(void)
{
    return g_vga_vram;
}

void vga_hw_blit_13h(const uint8_t *src,
                     uint16_t width,
                     uint16_t height,
                     uint16_t src_stride)
{
    uint16_t y;
    uint16_t copy_w;
    uint16_t copy_h;
    uint16_t dst_pitch;

    if (!src) {
        return;
    }
    dst_pitch = g_vga_pitch;
    if (dst_pitch == 0u) {
        return;
    }

    copy_w = width;
    copy_h = height;
    if (copy_w > g_vga_pitch) {
        copy_w = g_vga_pitch;
    }
    if (copy_h > g_vga_height) {
        copy_h = g_vga_height;
    }

    for (y = 0u; y < copy_h; ++y) {
        const uint8_t *src_row;
        uint8_t *dst_row;
        size_t row_bytes;

        src_row = src + ((size_t)y * (size_t)src_stride);
        dst_row = g_vga_vram + ((size_t)y * (size_t)dst_pitch);
        row_bytes = (size_t)copy_w;
        if (row_bytes > sizeof(g_vga_vram)) {
            row_bytes = sizeof(g_vga_vram);
        }
        memcpy(dst_row, src_row, row_bytes);
    }
}
