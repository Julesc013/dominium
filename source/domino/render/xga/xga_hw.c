#include "xga_hw.h"

#include <stddef.h>
#include <string.h>

/* Stub VRAM buffer to mirror writes in non-XGA environments. */
static uint8_t g_xga_vram[1024u * 1024u];
static uint32_t g_xga_vram_pitch = 0u;
static uint32_t g_xga_vram_height = 0u;

int xga_hw_init(void)
{
    /* Stub always succeeds. Real implementation would probe XGA hardware. */
    return 0;
}

int xga_hw_set_mode(uint16_t req_w, uint16_t req_h, xga_mode_info *out_mode)
{
    xga_mode_info mode;
    (void)req_w;
    (void)req_h;

    memset(&mode, 0, sizeof(mode));

    /* v1: pick between 640x480x8 and 800x600x8; default to 640x480. */
    mode.kind = XGA_MODE_KIND_640x480_8;
    mode.width = 640u;
    mode.height = 480u;
    if (req_w >= 800u && req_h >= 600u) {
        mode.kind = XGA_MODE_KIND_800x600_8;
        mode.width = 800u;
        mode.height = 600u;
    }
    mode.bpp = 8u;
    mode.pitch_bytes = mode.width;
    mode.phys_base = 0u;

    if (out_mode) {
        *out_mode = mode;
    }

    g_xga_vram_pitch = mode.pitch_bytes;
    g_xga_vram_height = mode.height;

    return 0;
}

void xga_hw_restore_mode(void)
{
    /* Stub: real implementation would restore previous video mode. */
}

void xga_hw_blit(const uint8_t *src,
                 uint16_t width,
                 uint16_t height,
                 uint16_t src_stride,
                 const xga_mode_info *mode)
{
    uint16_t y;
    uint16_t copy_w;
    uint16_t copy_h;
    uint32_t dst_pitch;

    (void)mode;

    if (!src || g_xga_vram_pitch == 0u) {
        return;
    }

    copy_w = width;
    copy_h = height;
    if (mode) {
        if (copy_w > mode->width)  copy_w = mode->width;
        if (copy_h > mode->height) copy_h = mode->height;
    }
    dst_pitch = (uint32_t)g_xga_vram_pitch;
    if (dst_pitch == 0u) {
        return;
    }

    for (y = 0u; y < copy_h; ++y) {
        const uint8_t *src_row;
        uint8_t *dst_row;
        size_t row_bytes;

        src_row = src + ((size_t)y * (size_t)src_stride);
        dst_row = g_xga_vram + ((size_t)y * (size_t)dst_pitch);
        row_bytes = (size_t)copy_w;
        if (row_bytes > sizeof(g_xga_vram)) {
            row_bytes = sizeof(g_xga_vram);
        }
        memcpy(dst_row, src_row, row_bytes);
    }

    (void)g_xga_vram_height;
}
