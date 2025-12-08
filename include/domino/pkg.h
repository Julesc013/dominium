#ifndef DOMINO_PKG_H_INCLUDED
#define DOMINO_PKG_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_pkg_registry dom_pkg_registry;

typedef enum dom_pkg_kind {
    DOM_PKG_UNKNOWN = 0,
    DOM_PKG_MOD,
    DOM_PKG_PACK,
    DOM_PKG_PRODUCT
} dom_pkg_kind;

typedef struct dom_pkg_info {
    uint32_t    struct_size;
    uint32_t    struct_version;
    char        id[64];
    uint32_t    version_major;
    uint32_t    version_minor;
    uint32_t    version_patch;
    dom_pkg_kind kind;
} dom_pkg_info;

typedef struct dom_pkg_registry_desc {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dsys_context*  sys;
    const char* const* search_roots;
    uint32_t       root_count;
} dom_pkg_registry_desc;

typedef int (*dom_pkg_enumerate_fn)(const dom_pkg_info* info, void* user_data);

dom_status dom_pkg_registry_create(const dom_pkg_registry_desc* desc, dom_pkg_registry** out_registry);
void       dom_pkg_registry_destroy(dom_pkg_registry* registry);
dom_status dom_pkg_registry_refresh(dom_pkg_registry* registry);
dom_status dom_pkg_registry_find(dom_pkg_registry* registry, const char* id, dom_pkg_info* out_info);
dom_status dom_pkg_registry_enumerate(dom_pkg_registry* registry, dom_pkg_enumerate_fn fn, void* user_data);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_PKG_H_INCLUDED */
