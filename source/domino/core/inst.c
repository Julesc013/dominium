#include "domino/inst.h"

#include <stdlib.h>
#include <string.h>

struct dom_inst {
    dom_inst_desc desc;
    int           resolved;
};

dom_status dom_inst_create(const dom_inst_desc* desc, dom_inst** out_inst)
{
    dom_inst* inst;
    dom_inst_desc local_desc;

    if (!out_inst) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_inst = NULL;

    inst = (dom_inst*)malloc(sizeof(dom_inst));
    if (!inst) {
        return DOM_STATUS_ERROR;
    }
    memset(inst, 0, sizeof(*inst));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }

    local_desc.struct_size = sizeof(dom_inst_desc);
    inst->desc = local_desc;
    inst->resolved = 0;

    *out_inst = inst;
    return DOM_STATUS_OK;
}

void dom_inst_destroy(dom_inst* inst)
{
    if (!inst) {
        return;
    }
    free(inst);
}

dom_status dom_inst_load(dom_inst* inst, const char* path)
{
    (void)inst;
    (void)path;
    return DOM_STATUS_OK;
}

dom_status dom_inst_save(dom_inst* inst, const char* path)
{
    (void)inst;
    (void)path;
    return DOM_STATUS_OK;
}

dom_status dom_inst_resolve(dom_inst* inst)
{
    if (!inst) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    inst->resolved = 1;
    return DOM_STATUS_OK;
}

dom_pkg_registry* dom_inst_get_registry(dom_inst* inst)
{
    if (!inst) {
        return NULL;
    }
    return inst->desc.registry;
}
