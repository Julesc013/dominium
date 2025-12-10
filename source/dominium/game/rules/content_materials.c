#include "dominium/content_materials.h"

dom_status dom_materials_register(const dom_material_desc* desc,
                                  dom_material_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

const dom_material_desc* dom_materials_get(dom_material_id id)
{
    (void)id;
    return (const dom_material_desc*)0;
}

uint32_t dom_materials_count(void)
{
    return 0;
}

dom_status dom_materials_visit(dom_material_visit_fn fn, void* user)
{
    (void)fn;
    (void)user;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_materials_reset(void)
{
}
