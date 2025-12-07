#ifndef DOM_RENDER_NULL_H
#define DOM_RENDER_NULL_H

#include "dom_render_api.h"

#ifdef __cplusplus
extern "C" {
#endif

const DomRenderBackendAPI *dom_render_backend_null(void);
const DomRenderBackendAPI *dom_render_backend_vector2d(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_RENDER_NULL_H */
