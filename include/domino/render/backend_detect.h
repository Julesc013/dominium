#ifndef DOMINO_RENDER_BACKEND_DETECT_H_INCLUDED
#define DOMINO_RENDER_BACKEND_DETECT_H_INCLUDED

#include "domino/core/types.h"
#include "domino/render/pipeline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_gfx_backend_info {
    d_gfx_backend_type backend;
    int                supported;
    char               name[64];
    char               detail[128];
} d_gfx_backend_info;

#define D_GFX_BACKEND_MAX 16

u32 d_gfx_detect_backends(d_gfx_backend_info* out_list, u32 max_count);
d_gfx_backend_type d_gfx_select_backend(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_RENDER_BACKEND_DETECT_H_INCLUDED */
