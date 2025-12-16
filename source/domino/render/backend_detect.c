/*
FILE: source/domino/render/backend_detect.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/backend_detect
RESPONSIBILITY: Implements `backend_detect`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/render/backend_detect.h"

#include <string.h>

static void d_gfx_backend_info_set(d_gfx_backend_info* info,
                                   d_gfx_backend_type backend,
                                   int supported,
                                   const char* name,
                                   const char* detail) {
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

u32 d_gfx_detect_backends(d_gfx_backend_info* out_list, u32 max_count) {
    u32 count = 0u;
    if (out_list && max_count > 0u) {
        d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_SOFT, 1, "Software", "Always available");
    }

#if defined(_WIN32)
    if (count < max_count) d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_DX9, 1, "DirectX 9", "Win32 stub detection");
    if (count < max_count) d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_DX11, 1, "DirectX 11", "Win32 stub detection");
    if (count < max_count) d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_GL1, 1, "OpenGL 1.x", "Win32 stub detection");
    if (count < max_count) d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_GL2, 1, "OpenGL 2.x", "Win32 stub detection");
#endif
#if defined(__APPLE__)
    if (count < max_count) d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_METAL, 1, "Metal", "Compile-time availability");
#endif
#if defined(__unix__) || defined(__unix) || defined(__APPLE__)
    if (count < max_count) d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_GL1, 1, "OpenGL 1.x", "POSIX stub detection");
    if (count < max_count) d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_GL2, 1, "OpenGL 2.x", "POSIX stub detection");
#endif
    /* Vulkan is optional; mark as potential if loader might exist */
#if defined(_WIN32) || defined(__linux__)
    if (count < max_count) d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_VK1, 1, "Vulkan 1.x", "Potential support (loader not probed)");
#endif

    if (count < max_count) {
        d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_VESA, 0, "VESA", "Retro backend not probed");
    }
    if (count < max_count) {
        d_gfx_backend_info_set(&out_list[count++], D_GFX_BACKEND_VGA, 0, "VGA", "Retro backend not probed");
    }

    return count;
}

static int d_gfx_backend_supported(const d_gfx_backend_info* infos, u32 count, d_gfx_backend_type backend) {
    u32 i;
    for (i = 0u; i < count; ++i) {
        if (infos[i].backend == backend) {
            return infos[i].supported ? 1 : 0;
        }
    }
    return 0;
}

d_gfx_backend_type d_gfx_select_backend(void) {
    d_gfx_backend_info infos[D_GFX_BACKEND_MAX];
    const d_gfx_backend_type preferred[] = {
        D_GFX_BACKEND_VK1,
        D_GFX_BACKEND_DX11,
        D_GFX_BACKEND_GL2,
        D_GFX_BACKEND_DX9,
        D_GFX_BACKEND_GL1,
        D_GFX_BACKEND_METAL,
        D_GFX_BACKEND_SOFT
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
