/*
FILE: include/render/d_gfx_caps.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / render/d_gfx_caps
RESPONSIBILITY: Defines the public contract for `d_gfx_caps`; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Capability masks are deterministic and fixed per backend build.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend by adding new opcode bits as IR grows.
*/
#ifndef D_GFX_CAPS_PUBLIC_H
#define D_GFX_CAPS_PUBLIC_H

#include "domino/core/types.h"
#include "domino/gfx.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DGFX_CAP_OP_CLEAR        (1u << D_GFX_OP_CLEAR)
#define DGFX_CAP_OP_SET_VIEWPORT (1u << D_GFX_OP_SET_VIEWPORT)
#define DGFX_CAP_OP_SET_CAMERA   (1u << D_GFX_OP_SET_CAMERA)
#define DGFX_CAP_OP_DRAW_RECT    (1u << D_GFX_OP_DRAW_RECT)
#define DGFX_CAP_OP_DRAW_TEXT    (1u << D_GFX_OP_DRAW_TEXT)

#define DGFX_CAP_OP_ALL (DGFX_CAP_OP_CLEAR | DGFX_CAP_OP_SET_VIEWPORT | \
                         DGFX_CAP_OP_SET_CAMERA | DGFX_CAP_OP_DRAW_RECT | \
                         DGFX_CAP_OP_DRAW_TEXT)

u32 d_gfx_get_opcode_mask(void);
u32 d_gfx_get_opcode_mask_for_backend(const char* name);
const char* d_gfx_get_backend_name(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_GFX_CAPS_PUBLIC_H */
