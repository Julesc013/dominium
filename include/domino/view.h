#ifndef DOMINO_VIEW_H_INCLUDED
#define DOMINO_VIEW_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_view_kind {
    DOM_VIEW_KIND_TABLE = 0,
    DOM_VIEW_KIND_TREE,
    DOM_VIEW_KIND_FORM,
    DOM_VIEW_KIND_CANVAS
} dom_view_kind;

typedef struct dom_view_desc {
    uint32_t      struct_size;
    uint32_t      struct_version;
    const char*   id;
    const char*   title;
    dom_view_kind kind;
    const char*   model_id;
} dom_view_desc;

uint32_t dom_ui_list_views(dom_core* core, dom_view_desc* out, uint32_t max_out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_VIEW_H_INCLUDED */
