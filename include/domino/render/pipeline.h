/*
FILE: include/domino/render/pipeline.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / render/pipeline
RESPONSIBILITY: Defines the public contract for `pipeline` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_RENDER_PIPELINE_H_INCLUDED
#define DOMINO_RENDER_PIPELINE_H_INCLUDED

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum d_gfx_backend_type {
    D_GFX_BACKEND_SOFT = 0,
    D_GFX_BACKEND_DX7,
    D_GFX_BACKEND_DX9,
    D_GFX_BACKEND_DX11,
    D_GFX_BACKEND_GL1,
    D_GFX_BACKEND_GL2,
    D_GFX_BACKEND_VK1,
    D_GFX_BACKEND_METAL,
    D_GFX_BACKEND_VESA,
    D_GFX_BACKEND_VGA,
    D_GFX_BACKEND_MAX_ENUM
} d_gfx_backend_type;

typedef struct d_gfx_pipeline d_gfx_pipeline;
typedef struct d_gfx_pass     d_gfx_pass;
typedef struct d_gfx_target   d_gfx_target;

typedef struct d_gfx_ir_command {
    u16        opcode;
    const void* payload;
    u32        payload_size;
} d_gfx_ir_command;

typedef struct d_gfx_material {
    u32 id;
} d_gfx_material;

d_gfx_material d_gfx_material_default(void);

d_gfx_pipeline* d_gfx_pipeline_create(d_gfx_backend_type backend);
void            d_gfx_pipeline_destroy(d_gfx_pipeline* pipe);

d_gfx_target*   d_gfx_target_create(d_gfx_pipeline* pipe, i32 width, i32 height);
void            d_gfx_target_destroy(d_gfx_pipeline* pipe, d_gfx_target* target);

d_gfx_pass*     d_gfx_pass_create(d_gfx_pipeline* pipe, d_gfx_target* target);
void            d_gfx_pass_destroy(d_gfx_pipeline* pipe, d_gfx_pass* pass);

void            d_gfx_pass_begin(d_gfx_pass* pass);
void            d_gfx_pass_end(d_gfx_pass* pass);
void            d_gfx_pass_submit_ir(d_gfx_pass* pass, const struct d_gfx_ir_command* cmds, u32 count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_RENDER_PIPELINE_H_INCLUDED */
