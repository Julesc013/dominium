/*
FILE: include/dominium/content_materials.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / content_materials
RESPONSIBILITY: Defines the public contract for `content_materials` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_CONTENT_MATERIALS_H
#define DOMINIUM_CONTENT_MATERIALS_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "domino/dmatter.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_material_id: Public type used by `content_materials`. */
typedef uint32_t dom_material_id;

/* dom_material_desc: Public type used by `content_materials`. */
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

/* Purpose: Register materials.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status              dom_materials_register(const dom_material_desc* desc,
                                               dom_material_id* out_id);
/* Purpose: Get materials.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const dom_material_desc* dom_materials_get(dom_material_id id);
/* Purpose: Count dom materials.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
uint32_t                dom_materials_count(void);
/* Purpose: Visit dom materials.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status              dom_materials_visit(dom_material_visit_fn fn,
                                            void* user);
/* Purpose: Reset dom materials.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void                    dom_materials_reset(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_CONTENT_MATERIALS_H */
