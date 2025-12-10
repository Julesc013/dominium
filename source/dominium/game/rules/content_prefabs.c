#include "dominium/content_prefabs.h"

dom_status dom_prefabs_register(const dom_prefab_desc* desc,
                                dom_prefab_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

const dom_prefab_desc* dom_prefabs_get(dom_prefab_id id)
{
    (void)id;
    return (const dom_prefab_desc*)0;
}

uint32_t dom_prefabs_count(void)
{
    return 0;
}

dom_status dom_prefabs_visit(dom_prefab_visit_fn fn, void* user)
{
    (void)fn;
    (void)user;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_prefabs_reset(void)
{
}
