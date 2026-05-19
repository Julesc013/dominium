/*
FILE: include/domino/view.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / view
RESPONSIBILITY: Defines the public contract for `view` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_VIEW_H_INCLUDED
#define DOMINO_VIEW_H_INCLUDED

#include "domino/baseline.h"
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_view_kind: Public type used by `view`. */
typedef enum dom_view_kind {
    DOM_VIEW_KIND_TABLE = 0,
    DOM_VIEW_KIND_TREE,
    DOM_VIEW_KIND_FORM,
    DOM_VIEW_KIND_CANVAS
} dom_view_kind;

/* dom_view_desc: Public type used by `view`. */
typedef struct dom_view_desc {
    uint32_t      struct_size;
    uint32_t      struct_version;
    const char*   id;
    const char*   title;
    dom_view_kind kind;
    const char*   model_id; /* table_id, tree_id, or canvas_id */
} dom_view_desc;

/* Purpose: Views dom ui list.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
uint32_t dom_ui_list_views(dom_core* core, dom_view_desc* out, uint32_t max_out);
/* Purpose: Register view.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool     dom_view_register(dom_core* core, const dom_view_desc* desc);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_VIEW_H_INCLUDED */
