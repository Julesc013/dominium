/* TODO: legacy render stub; replaced by domino_gfx + soft backend */
#include "dominium/dom_rend.h"

#include <stdlib.h>
#include <string.h>

struct dom_rend_device {
    int width;
    int height;
    uint32_t *pixels;
};

static dom_rend_device* soft_create(const struct dom_rend_desc* desc)
{
    dom_rend_device* dev;
    if (!desc) return 0;
    dev = (dom_rend_device*)malloc(sizeof(dom_rend_device));
    if (!dev) return 0;
    dev->width = desc->width;
    dev->height = desc->height;
    dev->pixels = (uint32_t*)malloc((size_t)desc->width * (size_t)desc->height * sizeof(uint32_t));
    if (dev->pixels) {
        memset(dev->pixels, 0, (size_t)desc->width * (size_t)desc->height * sizeof(uint32_t));
    }
    return dev;
}

static void soft_destroy(dom_rend_device* dev)
{
    if (!dev) return;
    if (dev->pixels) free(dev->pixels);
    free(dev);
}

static void soft_begin(dom_rend_device* dev) { (void)dev; }
static void soft_end(dom_rend_device* dev) { (void)dev; }

static void soft_clear(dom_rend_device* dev, uint32_t rgba)
{
    size_t n;
    size_t i;
    if (!dev || !dev->pixels) return;
    n = (size_t)dev->width * (size_t)dev->height;
    for (i = 0; i < n; ++i) {
        dev->pixels[i] = rgba;
    }
}

static void soft_draw_rect(dom_rend_device* dev, int x, int y, int w, int h, uint32_t rgba)
{
    int iy, ix;
    if (!dev || !dev->pixels) return;
    for (iy = 0; iy < h; ++iy) {
        int py = y + iy;
        if (py < 0 || py >= dev->height) continue;
        for (ix = 0; ix < w; ++ix) {
            int px = x + ix;
            if (px < 0 || px >= dev->width) continue;
            dev->pixels[(size_t)py * (size_t)dev->width + (size_t)px] = rgba;
        }
    }
}

static const struct dom_rend_vtable g_rend_soft = {
    DOM_REND_API_VERSION,
    soft_create,
    soft_destroy,
    soft_begin,
    soft_end,
    soft_clear,
    soft_draw_rect
};

const struct dom_rend_vtable* dom_rend_choose_best(void)
{
    return &g_rend_soft;
}
