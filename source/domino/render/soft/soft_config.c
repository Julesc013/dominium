/*
FILE: source/domino/render/soft/soft_config.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/soft_config
RESPONSIBILITY: Implements `soft_config`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "soft_config.h"

#include <string.h>

static void soft_features_set_all(dgfx_soft_features* f, uint8_t on)
{
    if (!f) {
        return;
    }
    f->enable_2d = on;
    f->enable_3d = on;
    f->enable_vector = on;
    f->enable_raster = on;
    f->enable_depth = on;
    f->enable_stencil = on;
    f->enable_blend = on;
    f->enable_texturing = on;
    f->enable_mipmaps = on;
    f->enable_gamma = on;
    f->enable_msaa = on;
    f->enable_subpixel = on;
}

void dgfx_soft_config_get_default(dgfx_soft_config* out_cfg)
{
    if (!out_cfg) {
        return;
    }

    memset(out_cfg, 0, sizeof(*out_cfg));
    out_cfg->profile = DGFX_SOFT_PROFILE_BALANCED;
    out_cfg->color_format = DGFX_SOFT_FMT_32_ARGB;
    out_cfg->depth_bits = 24u;
    out_cfg->stencil_bits = 0u;
    out_cfg->allow_resize = 1u;

    memset(&out_cfg->features, 0, sizeof(out_cfg->features));
    out_cfg->features.enable_depth = 1u;
    out_cfg->features.enable_2d = 1u;
    out_cfg->features.enable_vector = 1u;
    out_cfg->features.enable_raster = 1u;
    out_cfg->features.enable_3d = 1u;
    out_cfg->max_triangles_per_frame = 65536u;
    out_cfg->max_lines_per_frame = 65536u;
    out_cfg->max_sprites_per_frame = 32768u;
    out_cfg->prefer_fullscreen = 0u;
    out_cfg->prefer_borderless = 0u;
}

void dgfx_soft_config_apply_profile(dgfx_soft_config* cfg, dgfx_soft_profile profile)
{
    if (!cfg) {
        return;
    }

    cfg->profile = profile;

    switch (profile) {
    case DGFX_SOFT_PROFILE_FAST:
        cfg->color_format = DGFX_SOFT_FMT_16_565;
        cfg->depth_bits = 16u;
        cfg->stencil_bits = 0u;
        memset(&cfg->features, 0, sizeof(cfg->features));
        cfg->features.enable_depth = 1u;
        cfg->features.enable_2d = 1u;
        cfg->features.enable_vector = 1u;
        cfg->features.enable_raster = 1u;
        break;
    case DGFX_SOFT_PROFILE_REF:
        cfg->color_format = DGFX_SOFT_FMT_32_ARGB;
        cfg->depth_bits = 32u;
        cfg->stencil_bits = 0u;
        soft_features_set_all(&cfg->features, 1u);
        cfg->features.enable_blend = 1u;
        break;
    case DGFX_SOFT_PROFILE_BALANCED:
        cfg->color_format = DGFX_SOFT_FMT_32_ARGB;
        cfg->depth_bits = 24u;
        cfg->stencil_bits = 8u;
        memset(&cfg->features, 0, sizeof(cfg->features));
        cfg->features.enable_depth = 1u;
        cfg->features.enable_2d = 1u;
        cfg->features.enable_vector = 1u;
        cfg->features.enable_raster = 1u;
        cfg->features.enable_3d = 1u;
        break;
    case DGFX_SOFT_PROFILE_NULL:
    default:
        cfg->color_format = DGFX_SOFT_FMT_8_INDEXED;
        cfg->depth_bits = 0u;
        cfg->stencil_bits = 0u;
        soft_features_set_all(&cfg->features, 0u);
        break;
    }
}

void dgfx_soft_config_load_from_env(dgfx_soft_config* cfg)
{
    (void)cfg;
    /* Stub: real implementation would parse environment variables. */
}

void dgfx_soft_config_load_from_file(dgfx_soft_config* cfg, const char* path)
{
    (void)cfg;
    (void)path;
    /* Stub: configuration file parsing not implemented in this revision. */
}
