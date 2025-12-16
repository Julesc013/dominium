/*
FILE: include/dominium/content_prefabs.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / content_prefabs
RESPONSIBILITY: Defines the public contract for `content_prefabs` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_CONTENT_PREFABS_H
#define DOMINIUM_CONTENT_PREFABS_H

#include <stddef.h>
#include "domino/baseline.h"

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
