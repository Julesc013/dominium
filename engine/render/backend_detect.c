/*
FILE: source/domino/render/backend_detect.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/backend_detect
RESPONSIBILITY: Implements `backend_detect`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `include/render/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/render/backend_detect.h"

#include <string.h>

#include "domino/config_base.h"

static void d_gfx_backend_info_set(d_gfx_backend_info* info,
                                   d_gfx_backend_type backend,
                                   int supported,
                                   const char* name,
                                   const char* detail)
{
    if (!info) {
        return;
    }
    info->backend = backend;
    info->supported = supported;
    info->name[0] = '\0';
    info->detail[0] = '\0';
    if (name) {
        size_t len = strlen(name);
        if (len >= sizeof(info->name)) len = sizeof(info->name) - 1u;
        memcpy(info->name, name, len);
        info->name[len] = '\0';
    }
    if (detail) {
        size_t len = strlen(detail);
        if (len >= sizeof(info->detail)) len = sizeof(info->detail) - 1u;
        memcpy(info->detail, detail, len);
        info->detail[len] = '\0';
    }
}

static const char* d_gfx_detail_for(int supported, const char* enabled_detail, const char* disabled_detail)
{
    return supported ? enabled_detail : disabled_detail;
}

u32 d_gfx_detect_backends(d_gfx_backend_info* out_list, u32 max_count)
{
    u32 count = 0u;
    if (!out_list || max_count == 0u) {
        return 0u;
    }

    if (count < max_count) {
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_SOFT,
            DOM_BACKEND_SOFT,
            "soft",
            d_gfx_detail_for(DOM_BACKEND_SOFT, "Built-in software backend", "Disabled at build"));
    }

    if (count < max_count) {
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_NULL,
            DOM_BACKEND_NULL,
            "null",
            d_gfx_detail_for(DOM_BACKEND_NULL, "Headless null backend", "Disabled at build"));
    }

    if (count < max_count) {
        int built = DOM_BACKEND_DX9 ? 1 : 0;
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_DX9,
            built,
            "dx9",
            built ? "Soft-backed stub (software raster)" : "Disabled at build");
    }

    if (count < max_count) {
        int built = DOM_BACKEND_DX11 ? 1 : 0;
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_DX11,
            built,
            "dx11",
            built ? "Soft-backed stub (software raster)" : "Disabled at build");
    }

    if (count < max_count) {
        int built = DOM_BACKEND_GL2 ? 1 : 0;
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_GL2,
            built,
            "gl2",
            built ? "Soft-backed stub (software raster)" : "Disabled at build");
    }

    if (count < max_count) {
        int built = DOM_BACKEND_VK1 ? 1 : 0;
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_VK1,
            built,
            "vk1",
            built ? "Soft-backed stub (software raster)" : "Disabled at build");
    }

    if (count < max_count) {
        int built = DOM_BACKEND_METAL ? 1 : 0;
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_METAL,
            built,
            "metal",
            built ? "Soft-backed stub (software raster)" : "Disabled at build");
    }

    if (count < max_count) {
        int built = DOM_BACKEND_SOFT ? 1 : 0;
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_VESA,
            built,
            "vesa",
            built ? "Soft-backed stub (bare-metal)" : "Disabled at build");
    }

    if (count < max_count) {
        int built = DOM_BACKEND_SOFT ? 1 : 0;
        d_gfx_backend_info_set(
            &out_list[count++],
            D_GFX_BACKEND_VGA,
            built,
            "vga",
            built ? "Soft-backed stub (bare-metal)" : "Disabled at build");
    }

    return count;
}

static int d_gfx_backend_supported(const d_gfx_backend_info* infos, u32 count, d_gfx_backend_type backend)
{
    u32 i;
    for (i = 0u; i < count; ++i) {
        if (infos[i].backend == backend) {
            return infos[i].supported ? 1 : 0;
        }
    }
    return 0;
}

d_gfx_backend_type d_gfx_select_backend(void)
{
    d_gfx_backend_info infos[D_GFX_BACKEND_MAX];
    const d_gfx_backend_type preferred[] = {
        D_GFX_BACKEND_SOFT,
        D_GFX_BACKEND_DX11,
        D_GFX_BACKEND_DX9,
        D_GFX_BACKEND_GL2,
        D_GFX_BACKEND_VK1,
        D_GFX_BACKEND_METAL,
        D_GFX_BACKEND_NULL
    };
    u32 detected = d_gfx_detect_backends(infos, (u32)(sizeof(infos) / sizeof(infos[0])));
    u32 i;
    for (i = 0u; i < (u32)(sizeof(preferred) / sizeof(preferred[0])); ++i) {
        if (d_gfx_backend_supported(infos, detected, preferred[i])) {
            return preferred[i];
        }
    }
    return D_GFX_BACKEND_SOFT;
}
