#ifndef DOMINO_PKG_H_INCLUDED
#define DOMINO_PKG_H_INCLUDED

#include <stddef.h>
#include <stdint.h>
#include "domino/core.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t dom_package_id;

typedef enum dom_package_kind {
    DOM_PKG_KIND_UNKNOWN = 0,
    DOM_PKG_KIND_MOD,
    DOM_PKG_KIND_CONTENT,
    DOM_PKG_KIND_PRODUCT
} dom_package_kind;

#define DOM_MAX_PACKAGE_DEPS 8

typedef struct dom_package_info {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_package_id   id;
    dom_package_kind kind;
    char             name[64];
    char             version[32];
    char             author[64];
    char             install_path[260];
    uint32_t         dep_count;
    dom_package_id   deps[DOM_MAX_PACKAGE_DEPS];
    char             game_version_min[32];
    char             game_version_max[32];
} dom_package_info;

uint32_t dom_pkg_list(dom_core* core, dom_package_info* out, uint32_t max_out);
bool     dom_pkg_get(dom_core* core, dom_package_id id, dom_package_info* out);
bool     dom_pkg_install(dom_core* core, const char* source_path, dom_package_id* out_id);
bool     dom_pkg_uninstall(dom_core* core, dom_package_id id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_PKG_H_INCLUDED */
