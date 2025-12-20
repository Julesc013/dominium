/*
FILE: source/domino/render/soft/soft_config.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/soft_config
RESPONSIBILITY: Defines internal contract for `soft_config`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_SOFT_CONFIG_H
#define DOMINIUM_SOFT_CONFIG_H

#include <stdint.h>

/* Render profile */
typedef enum dgfx_soft_profile_t {
    DGFX_SOFT_PROFILE_NULL = 0,      /* no rendering at all, replaces 'null' backend */
    DGFX_SOFT_PROFILE_FAST,
    DGFX_SOFT_PROFILE_BALANCED,
    DGFX_SOFT_PROFILE_REF
} dgfx_soft_profile;
#define DGFX_SOFT_PROFILE_REFERENCE DGFX_SOFT_PROFILE_REF

/* Pixel formats supported by the software backend */
typedef enum dgfx_soft_format_t {
    DGFX_SOFT_FMT_8_INDEXED = 0,     /* 8bpp paletted */
    DGFX_SOFT_FMT_16_565,            /* 16bpp RGB565 */
    DGFX_SOFT_FMT_32_ARGB            /* 32bpp ARGB/RGBA (implementation-defined order) */
} dgfx_soft_format;

/* Feature flags (each can be toggled independently) */
typedef struct dgfx_soft_features_t {
    uint8_t enable_2d;
    uint8_t enable_3d;
    uint8_t enable_vector;
    uint8_t enable_raster;
    uint8_t enable_depth;
    uint8_t enable_stencil;
    uint8_t enable_blend;
    uint8_t enable_texturing;
    uint8_t enable_mipmaps;
    uint8_t enable_gamma;
    uint8_t enable_msaa;
    uint8_t enable_subpixel;
    uint8_t reserved[3];
} dgfx_soft_features;

/* Main configuration struct */
typedef struct dgfx_soft_config_t {
    dgfx_soft_profile profile;
    dgfx_soft_format  color_format;
    uint8_t           depth_bits;      /* 0, 16, 24, 32 */
    uint8_t           stencil_bits;    /* 0 or 8 */
    uint8_t           allow_resize;    /* if 0, clamp to initial size */
    uint8_t           pad0;

    dgfx_soft_features features;

    /* Tuning knobs */
    uint32_t max_triangles_per_frame;
    uint32_t max_lines_per_frame;
    uint32_t max_sprites_per_frame;

    /* Present mode hints; actual fullscreen/windowed handled by dsys/backend */
    uint8_t prefer_fullscreen;
    uint8_t prefer_borderless;
    uint8_t pad1[2];

    /* Reserved for future extensions */
    uint32_t reserved_u32[8];
} dgfx_soft_config;

/* Internal API */
void dgfx_soft_config_get_default(dgfx_soft_config* out_cfg);
void dgfx_soft_config_apply_profile(dgfx_soft_config* cfg, dgfx_soft_profile profile);
void dgfx_soft_config_load_from_env(dgfx_soft_config* cfg);
void dgfx_soft_config_load_from_file(dgfx_soft_config* cfg, const char* path);

#endif /* DOMINIUM_SOFT_CONFIG_H */
