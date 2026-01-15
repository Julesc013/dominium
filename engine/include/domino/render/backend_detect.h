/*
FILE: include/domino/render/backend_detect.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / render/backend_detect
RESPONSIBILITY: Defines the public contract for `backend_detect` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_RENDER_BACKEND_DETECT_H_INCLUDED
#define DOMINO_RENDER_BACKEND_DETECT_H_INCLUDED

#include "domino/core/types.h"
#include "domino/render/pipeline.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_gfx_backend_info: Public type used by `backend_detect`. */
typedef struct d_gfx_backend_info {
    d_gfx_backend_type backend;
    int                supported;
    char               name[64];
    char               detail[128];
} d_gfx_backend_info;

#define D_GFX_BACKEND_MAX 16

/* Purpose: Backends d gfx detect.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
u32 d_gfx_detect_backends(d_gfx_backend_info* out_list, u32 max_count);
/* Purpose: Backend d gfx select.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
d_gfx_backend_type d_gfx_select_backend(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_RENDER_BACKEND_DETECT_H_INCLUDED */
