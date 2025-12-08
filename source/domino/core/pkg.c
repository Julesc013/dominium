#include "domino/pkg.h"

#include <stdlib.h>
#include <string.h>

struct dom_pkg_registry {
    dom_pkg_registry_desc desc;
};

dom_status dom_pkg_registry_create(const dom_pkg_registry_desc* desc, dom_pkg_registry** out_registry)
{
    dom_pkg_registry* reg;
    dom_pkg_registry_desc local_desc;

    if (!out_registry) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_registry = NULL;

    reg = (dom_pkg_registry*)malloc(sizeof(dom_pkg_registry));
    if (!reg) {
        return DOM_STATUS_ERROR;
    }
    memset(reg, 0, sizeof(*reg));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }

    local_desc.struct_size = sizeof(dom_pkg_registry_desc);
    reg->desc = local_desc;

    *out_registry = reg;
    return DOM_STATUS_OK;
}

void dom_pkg_registry_destroy(dom_pkg_registry* registry)
{
    if (!registry) {
        return;
    }
    free(registry);
}

dom_status dom_pkg_registry_refresh(dom_pkg_registry* registry)
{
    (void)registry;
    return DOM_STATUS_OK;
}

dom_status dom_pkg_registry_find(dom_pkg_registry* registry, const char* id, dom_pkg_info* out_info)
{
    (void)registry;
    (void)id;
    if (out_info) {
        memset(out_info, 0, sizeof(*out_info));
        out_info->struct_size = sizeof(dom_pkg_info);
        out_info->struct_version = 1u;
    }
    return DOM_STATUS_NOT_FOUND;
}

dom_status dom_pkg_registry_enumerate(dom_pkg_registry* registry, dom_pkg_enumerate_fn fn, void* user_data)
{
    (void)registry;
    (void)fn;
    (void)user_data;
    return DOM_STATUS_OK;
}
