#include "cga_hw.h"

#include <string.h>

static uint8_t g_cga_vram[80u * 200u];

int cga_hw_init(void)
{
    return 0;
}

int cga_hw_set_mode_320x200_4col(uint8_t palette, cga_mode_info* out_mode)
{
    if (out_mode) {
        memset(out_mode, 0, sizeof(*out_mode));
        out_mode->kind = CGA_MODE_KIND_320x200_4COL;
        out_mode->width = 320u;
        out_mode->height = 200u;
        out_mode->logical_bpp = 2u;
        out_mode->palette = (uint8_t)(palette ? 1u : 0u);
        out_mode->pitch_bytes = 80u;
        out_mode->vram_segment = 0xb800u;
    }
    return 0;
}

void cga_hw_restore_text_mode(void)
{
    /* Stub: real implementation would reset INT 10h mode 3. */
}

void cga_hw_blit_320x200_4col(const uint8_t* src,
                              uint16_t width,
                              uint16_t height,
                              uint16_t src_stride)
{
    uint16_t y;
    uint16_t dst_pitch;
    uint16_t use_w;
    uint16_t use_h;

    if (!src) {
        return;
    }

    use_w = (width > 320u) ? 320u : width;
    use_h = (height > 200u) ? 200u : height;
    dst_pitch = 80u;

    memset(g_cga_vram, 0, sizeof(g_cga_vram));

    for (y = 0u; y < use_h; ++y) {
        const uint8_t* src_row;
        uint8_t* dst_row;
        uint16_t x_byte;
        uint16_t dst_bytes;

        src_row = src + (size_t)y * (size_t)src_stride;
        dst_row = g_cga_vram + (size_t)y * (size_t)dst_pitch;
        dst_bytes = (uint16_t)((use_w + 3u) / 4u);

        for (x_byte = 0u; x_byte < dst_bytes; ++x_byte) {
            uint16_t base;
            uint8_t p0;
            uint8_t p1;
            uint8_t p2;
            uint8_t p3;

            base = (uint16_t)(x_byte * 4u);
            p0 = (base + 0u < use_w) ? (uint8_t)(src_row[base + 0u] & 0x03u) : 0u;
            p1 = (base + 1u < use_w) ? (uint8_t)(src_row[base + 1u] & 0x03u) : 0u;
            p2 = (base + 2u < use_w) ? (uint8_t)(src_row[base + 2u] & 0x03u) : 0u;
            p3 = (base + 3u < use_w) ? (uint8_t)(src_row[base + 3u] & 0x03u) : 0u;

            dst_row[x_byte] = (uint8_t)((p0 << 6) | (p1 << 4) | (p2 << 2) | (p3 << 0));
        }
    }

    (void)g_cga_vram;
}
