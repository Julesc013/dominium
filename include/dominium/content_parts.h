#ifndef DOMINIUM_CONTENT_PARTS_H
#define DOMINIUM_CONTENT_PARTS_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "dominium/content_materials.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t dom_part_id;

typedef enum dom_part_kind {
    DOM_PART_KIND_UNKNOWN = 0,
    DOM_PART_KIND_BLOCK,
    DOM_PART_KIND_BEAM,
    DOM_PART_KIND_MACHINE,
    DOM_PART_KIND_DECORATION
} dom_part_kind;

typedef struct dom_part_desc {
    uint32_t       struct_size;
    uint32_t       struct_version;
    const char*    name;
    dom_part_kind  kind;
    dom_material_id default_material;
    uint32_t       mass_grams;
    uint32_t       flags;
} dom_part_desc;

typedef int (*dom_part_visit_fn)(dom_part_id id,
                                 const dom_part_desc* desc,
                                 void* user);

dom_status           dom_parts_register(const dom_part_desc* desc,
                                        dom_part_id* out_id);
const dom_part_desc* dom_parts_get(dom_part_id id);
uint32_t             dom_parts_count(void);
dom_status           dom_parts_visit(dom_part_visit_fn fn, void* user);
void                 dom_parts_reset(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_CONTENT_PARTS_H */
