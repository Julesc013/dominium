#include "ega_hw.h"

#include <string.h>

#define EGA_PLANE_PITCH_BYTES 80u
#define EGA_MAX_HEIGHT        350u
#define EGA_MAX_WIDTH         640u

static uint8_t g_ega_vram[4u * EGA_PLANE_PITCH_BYTES * EGA_MAX_HEIGHT];

int ega_hw_init(void)
{
    return 0;
}

int ega_hw_set_mode_640x350_16(ega_mode_info* out_mode)
{
    if (out_mode) {
        memset(out_mode, 0, sizeof(*out_mode));
        out_mode->kind = EGA_MODE_KIND_640x350_16;
        out_mode->width = 640u;
        out_mode->height = 350u;
        out_mode->logical_bpp = 4u;
        out_mode->pitch_bytes = EGA_PLANE_PITCH_BYTES;
        out_mode->vram_segment = 0xa000u;
    }
    return 0;
}

void ega_hw_restore_text_mode(void)
{
    /* Stub: real implementation would invoke INT 10h mode restore. */
}

void ega_hw_blit_640x350_16(const uint8_t* src,
                            uint16_t width,
                            uint16_t height,
                            uint16_t src_stride)
{
    uint16_t use_w;
    uint16_t use_h;
    uint16_t y;
    size_t plane_size;

    if (!src) {
        return;
    }

    use_w = (width > EGA_MAX_WIDTH) ? EGA_MAX_WIDTH : width;
    use_h = (height > EGA_MAX_HEIGHT) ? EGA_MAX_HEIGHT : height;

    plane_size = (size_t)EGA_PLANE_PITCH_BYTES * (size_t)EGA_MAX_HEIGHT;
    memset(g_ega_vram, 0, plane_size * 4u);

    for (y = 0u; y < use_h; ++y) {
        const uint8_t* src_row;
        uint16_t dst_bytes;
        uint16_t x_byte;
        src_row = src + (size_t)y * (size_t)src_stride;
        dst_bytes = (uint16_t)((use_w + 7u) / 8u);

        for (x_byte = 0u; x_byte < dst_bytes; ++x_byte) {
            uint8_t packed[4];
            uint16_t base;
            int bit;

            packed[0] = packed[1] = packed[2] = packed[3] = 0u;
            base = (uint16_t)(x_byte * 8u);

            for (bit = 0; bit < 8; ++bit) {
                uint16_t px;
                uint8_t idx;
                int plane;

                px = (uint16_t)(base + (uint16_t)bit);
                if (px >= use_w) {
                    break;
                }
                idx = (uint8_t)(src_row[px] & 0x0fu);
                for (plane = 0; plane < 4; ++plane) {
                    uint8_t bit_val;
                    bit_val = (uint8_t)((idx >> plane) & 0x01u);
                    packed[plane] |= (uint8_t)(bit_val << (7 - bit));
                }
            }

            for (bit = 0; bit < 4; ++bit) {
                uint8_t* dst_row;
                dst_row = g_ega_vram + plane_size * (size_t)bit + (size_t)y * (size_t)EGA_PLANE_PITCH_BYTES;
                dst_row[x_byte] = packed[bit];
            }
        }
    }

    (void)g_ega_vram;
}
