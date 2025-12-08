#ifndef DOMINO_VIEW_H_INCLUDED
#define DOMINO_VIEW_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_view_registry dom_view_registry;

typedef enum dom_view_kind {
    DOM_VIEW_KIND_NONE = 0,
    DOM_VIEW_KIND_CANVAS = 1,
    DOM_VIEW_KIND_TABLE = 2,
    DOM_VIEW_KIND_TREE  = 3,
    DOM_VIEW_KIND_CUSTOM = 4
} dom_view_kind;

typedef struct dom_view_desc {
    uint32_t      struct_size;
    uint32_t      struct_version;
    const char*   id;
    const char*   title;
    dom_view_kind kind;
    void*         user_data;
} dom_view_desc;

typedef struct dom_view_registry_desc {
    uint32_t struct_size;
    uint32_t struct_version;
} dom_view_registry_desc;

dom_status dom_view_registry_create(const dom_view_registry_desc* desc, dom_view_registry** out_registry);
void       dom_view_registry_destroy(dom_view_registry* registry);
dom_status dom_view_register(dom_view_registry* registry, const dom_view_desc* desc);
dom_status dom_view_unregister(dom_view_registry* registry, const char* id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_VIEW_H_INCLUDED */
