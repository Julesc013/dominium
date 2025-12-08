#ifndef DOMINO_INST_H_INCLUDED
#define DOMINO_INST_H_INCLUDED

#include <stddef.h>
#include <stdint.h>
#include "domino/core.h"
#include "domino/pkg.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t dom_instance_id;

#define DOM_MAX_INSTANCE_PACKAGES 8

typedef struct dom_instance_info {
    uint32_t        struct_size;
    uint32_t        struct_version;
    dom_instance_id id;
    char            name[64];
    char            path[260];
    uint32_t        flags;
    uint32_t        pkg_count;
    dom_package_id  pkgs[DOM_MAX_INSTANCE_PACKAGES];
} dom_instance_info;

uint32_t        dom_inst_list(dom_core* core, dom_instance_info* out, uint32_t max_out);
bool            dom_inst_get(dom_core* core, dom_instance_id id, dom_instance_info* out);
dom_instance_id dom_inst_create(dom_core* core, const dom_instance_info* desc);
bool            dom_inst_update(dom_core* core, const dom_instance_info* desc);
bool            dom_inst_delete(dom_core* core, dom_instance_id id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_INST_H_INCLUDED */
