#include "domino/view.h"

#include <stdlib.h>
#include <string.h>

struct dom_view_registry {
    dom_view_registry_desc desc;
    uint32_t               view_count;
};

dom_status dom_view_registry_create(const dom_view_registry_desc* desc, dom_view_registry** out_registry)
{
    dom_view_registry* reg;
    dom_view_registry_desc local_desc;

    if (!out_registry) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_registry = NULL;

    reg = (dom_view_registry*)malloc(sizeof(dom_view_registry));
    if (!reg) {
        return DOM_STATUS_ERROR;
    }
    memset(reg, 0, sizeof(*reg));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }
    local_desc.struct_size = sizeof(dom_view_registry_desc);
    reg->desc = local_desc;
    reg->view_count = 0u;

    *out_registry = reg;
    return DOM_STATUS_OK;
}

void dom_view_registry_destroy(dom_view_registry* registry)
{
    if (!registry) {
        return;
    }
    free(registry);
}

dom_status dom_view_register(dom_view_registry* registry, const dom_view_desc* desc)
{
    (void)desc;
    if (!registry) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    registry->view_count += 1u;
    return DOM_STATUS_OK;
}

dom_status dom_view_unregister(dom_view_registry* registry, const char* id)
{
    (void)id;
    if (!registry) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    if (registry->view_count > 0u) {
        registry->view_count -= 1u;
    }
    return DOM_STATUS_OK;
}
