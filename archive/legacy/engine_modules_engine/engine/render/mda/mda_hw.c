/*
FILE: source/domino/render/mda/mda_hw.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/mda/mda_hw
RESPONSIBILITY: Implements `mda_hw`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "mda_hw.h"

#include <stddef.h>
#include <string.h>

/* Stub VRAM buffer for non-DOS targets; sized for a single 32KB page. */
#define MDA_VRAM_SIZE 0x8000u

static uint8_t g_mda_vram[MDA_VRAM_SIZE];

int mda_hw_init(void)
{
    memset(g_mda_vram, 0, sizeof(g_mda_vram));
    return 0;
}

int mda_hw_set_mode_720x350(mda_mode_info *out_mode)
{
    if (!out_mode) {
        return -1;
    }

    memset(out_mode, 0, sizeof(*out_mode));
    out_mode->kind = MDA_MODE_KIND_720x350_1;
    out_mode->width = 720u;
    out_mode->height = 350u;
    out_mode->bits_per_pixel = 1u;
    out_mode->pitch_bytes = (uint16_t)((out_mode->width + 7u) / 8u);
    out_mode->vram_segment = 0xb000u;
    return 0;
}

void mda_hw_restore_text_mode(void)
{
    /* Stub: real DOS implementation would restore 80x25 text. */
}

void mda_hw_blit_720x350(const uint8_t *src,
                         uint16_t width,
                         uint16_t height,
                         uint16_t stride_bytes)
{
    uint16_t pitch_bytes;
    uint16_t y;

    if (!src) {
        return;
    }

    pitch_bytes = (uint16_t)((width + 7u) / 8u);

    for (y = 0u; y < height; ++y) {
        uint16_t bank;
        uint16_t row_in_bank;
        uint32_t dst_offset;
        const uint8_t *src_row;
        uint16_t xb;

        bank = (uint16_t)(y & 3u);
        row_in_bank = (uint16_t)(y >> 2);
        dst_offset = (uint32_t)bank * 0x2000u + (uint32_t)row_in_bank * (uint32_t)pitch_bytes;
        if (dst_offset >= MDA_VRAM_SIZE) {
            break;
        }

        src_row = src + (size_t)y * (size_t)stride_bytes;

        for (xb = 0u; xb < pitch_bytes; ++xb) {
            uint8_t packed;
            uint16_t bit;
            packed = 0u;

            for (bit = 0u; bit < 8u; ++bit) {
                uint16_t px = (uint16_t)(xb * 8u + bit);
                if (px < width) {
                    if (src_row[px] >= 128u) {
                        packed |= (uint8_t)(0x80u >> bit);
                    }
                }
            }

            if (dst_offset + xb < MDA_VRAM_SIZE) {
                g_mda_vram[dst_offset + xb] = packed;
            }
        }
    }
}
