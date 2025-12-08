#include "dominium/content_parts.h"

dom_status dom_parts_register(const dom_part_desc* desc, dom_part_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

const dom_part_desc* dom_parts_get(dom_part_id id)
{
    (void)id;
    return (const dom_part_desc*)0;
}

uint32_t dom_parts_count(void)
{
    return 0;
}

dom_status dom_parts_visit(dom_part_visit_fn fn, void* user)
{
    (void)fn;
    (void)user;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_parts_reset(void)
{
}
