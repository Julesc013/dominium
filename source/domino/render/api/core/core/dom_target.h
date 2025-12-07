#ifndef DOM_TARGET_H
#define DOM_TARGET_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef dom_u32 dom_target_id;
#define DOM_TARGET_ID_INVALID ((dom_target_id)0u)

typedef enum dom_target_type_e {
    DOM_TARGET_WINDOW_BACKBUFFER = 0,
    DOM_TARGET_OFFSCREEN_TEXTURE = 1
} dom_target_type;

typedef struct dom_target_s {
    dom_target_type type;
    dom_u32 width;
    dom_u32 height;
    void *platform_window; /* opaque window handle for backbuffer targets */
} dom_target;

dom_target_id dom_target_create_backbuffer(void *platform_window,
                                           dom_u32 width,
                                           dom_u32 height);
dom_target_id dom_target_create_offscreen(dom_u32 width, dom_u32 height);
dom_err_t     dom_target_destroy(dom_target_id id);
dom_target   *dom_target_lookup(dom_target_id id);

#ifdef __cplusplus
}
#endif

#endif /* DOM_TARGET_H */
