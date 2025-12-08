#ifndef DOMINIUM_CONTENT_MATERIALS_H
#define DOMINIUM_CONTENT_MATERIALS_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "domino/dmatter.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t dom_material_id;

typedef struct dom_material_desc {
    uint32_t    struct_size;
    uint32_t    struct_version;
    const char* name;
    MaterialId  engine_material;
    uint32_t    flags;
} dom_material_desc;

typedef int (*dom_material_visit_fn)(dom_material_id id,
                                     const dom_material_desc* desc,
                                     void* user);

dom_status              dom_materials_register(const dom_material_desc* desc,
                                               dom_material_id* out_id);
const dom_material_desc* dom_materials_get(dom_material_id id);
uint32_t                dom_materials_count(void);
dom_status              dom_materials_visit(dom_material_visit_fn fn,
                                            void* user);
void                    dom_materials_reset(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_CONTENT_MATERIALS_H */
