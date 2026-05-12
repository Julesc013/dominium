/*
FILE: source/domino/render/herc/herc_hw.c
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
#include "herc_hw.h"

#include <string.h>

/* Stub VRAM buffer to avoid poking real hardware from hosted builds. */
static uint8_t g_herc_vram[0x8000u]; /* 32 KiB */

int herc_hw_init(void)
{
    return 0;
}

int herc_hw_set_mode_720x348(herc_mode_info* out_mode)
{
    if (out_mode) {
        memset(out_mode, 0, sizeof(*out_mode));
        out_mode->kind = HERC_MODE_KIND_720x348_1;
        out_mode->width = 720u;
        out_mode->height = 348u;
        out_mode->bits_per_pixel = 1u;
        out_mode->pitch_bytes = 90u; /* 720 / 8 */
        out_mode->vram_segment = 0xb000u;
    }
    return 0;
}

void herc_hw_restore_text_mode(void)
{
    /* Stub: real implementation would reset INT 10h mode 3. */
}

void herc_hw_blit_720x348(const uint8_t* src,
                          uint16_t width,
                          uint16_t height,
                          uint16_t src_stride)
{
    uint16_t use_w;
    uint16_t use_h;
    uint16_t y;
    const uint8_t threshold = 128u;
    const uint16_t dst_pitch = 90u;

    if (!src || src_stride == 0u) {
        return;
    }

    use_w = (width > 720u) ? 720u : width;
    use_h = (height > 348u) ? 348u : height;

    memset(g_herc_vram, 0, sizeof(g_herc_vram));

    for (y = 0u; y < use_h; ++y) {
        const uint8_t* src_row;
        uint8_t* dst_row;
        uint16_t bank;
        uint16_t row_index;
        size_t dst_offset;
        uint16_t dst_bytes;
        uint16_t x_byte;

        src_row = src + ((size_t)y * (size_t)src_stride);
        bank = (uint16_t)(y & 3u);      /* interlaced banks every 4th scanline */
        row_index = (uint16_t)(y >> 2); /* y / 4 */
        dst_offset = ((size_t)bank * 0x2000u) + ((size_t)row_index * (size_t)dst_pitch);
        if (dst_offset + dst_pitch > sizeof(g_herc_vram)) {
            continue;
        }
        dst_row = g_herc_vram + dst_offset;
        dst_bytes = (uint16_t)((use_w + 7u) / 8u);

        for (x_byte = 0u; x_byte < dst_bytes; ++x_byte) {
            uint16_t base = (uint16_t)(x_byte * 8u);
            uint8_t packed = 0u;
            uint16_t bit;
            for (bit = 0u; bit < 8u; ++bit) {
                uint16_t px = (uint16_t)(base + bit);
                uint8_t on = 0u;
                if (px < use_w) {
                    on = (src_row[px] >= threshold) ? 1u : 0u;
                }
                packed |= (uint8_t)(on << (7u - bit));
            }
            dst_row[x_byte] = packed;
        }
    }

    (void)g_herc_vram;
}
