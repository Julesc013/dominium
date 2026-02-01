/*
FILE: include/dominium/content_parts.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / content_parts
RESPONSIBILITY: Defines the public contract for `content_parts` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_CONTENT_PARTS_H
#define DOMINIUM_CONTENT_PARTS_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "dominium/content_materials.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_part_id: Public type used by `content_parts`. */
typedef uint32_t dom_part_id;

/* dom_part_kind: Public type used by `content_parts`. */
typedef enum dom_part_kind {
    DOM_PART_KIND_UNKNOWN = 0,
    DOM_PART_KIND_BLOCK,
    DOM_PART_KIND_BEAM,
    DOM_PART_KIND_MACHINE,
    DOM_PART_KIND_DECORATION
} dom_part_kind;

/* dom_part_desc: Public type used by `content_parts`. */
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

/* Purpose: Register parts.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status           dom_parts_register(const dom_part_desc* desc,
                                        dom_part_id* out_id);
/* Purpose: Get parts.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const dom_part_desc* dom_parts_get(dom_part_id id);
/* Purpose: Count dom parts.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
uint32_t             dom_parts_count(void);
/* Purpose: Visit dom parts.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status           dom_parts_visit(dom_part_visit_fn fn, void* user);
/* Purpose: Reset dom parts.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void                 dom_parts_reset(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_CONTENT_PARTS_H */
