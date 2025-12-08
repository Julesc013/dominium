#ifndef DOMINIUM_CONTENT_PREFABS_H
#define DOMINIUM_CONTENT_PREFABS_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "dominium/content_parts.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t dom_prefab_id;

typedef struct dom_prefab_desc {
    uint32_t        struct_size;
    uint32_t        struct_version;
    const char*     name;
    dom_part_id     root_part;
    uint32_t        part_count;
    const dom_part_id* part_ids;
    uint32_t        flags;
} dom_prefab_desc;

typedef int (*dom_prefab_visit_fn)(dom_prefab_id id,
                                   const dom_prefab_desc* desc,
                                   void* user);

dom_status            dom_prefabs_register(const dom_prefab_desc* desc,
                                           dom_prefab_id* out_id);
const dom_prefab_desc* dom_prefabs_get(dom_prefab_id id);
uint32_t              dom_prefabs_count(void);
dom_status            dom_prefabs_visit(dom_prefab_visit_fn fn, void* user);
void                  dom_prefabs_reset(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_CONTENT_PREFABS_H */
