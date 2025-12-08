#ifndef DOMINO_INST_H_INCLUDED
#define DOMINO_INST_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"
#include "domino/pkg.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_inst dom_inst;

typedef struct dom_inst_desc {
    uint32_t          struct_size;
    uint32_t          struct_version;
    const char*       id;
    const char*       label;
    dom_pkg_registry* registry;
    const char*       root_path;
} dom_inst_desc;

dom_status dom_inst_create(const dom_inst_desc* desc, dom_inst** out_inst);
void       dom_inst_destroy(dom_inst* inst);
dom_status dom_inst_load(dom_inst* inst, const char* path);
dom_status dom_inst_save(dom_inst* inst, const char* path);
dom_status dom_inst_resolve(dom_inst* inst);
dom_pkg_registry* dom_inst_get_registry(dom_inst* inst);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_INST_H_INCLUDED */
