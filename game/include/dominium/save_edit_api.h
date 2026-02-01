/*
FILE: include/dominium/save_edit_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / save_edit_api
RESPONSIBILITY: Defines the public contract for `save_edit_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_SAVE_EDIT_API_H_INCLUDED
#define DOMINIUM_SAVE_EDIT_API_H_INCLUDED

#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_save_edit_ctx: Public type used by `save_edit_api`. */
typedef struct dom_save_edit_ctx_t dom_save_edit_ctx;

/* dom_save_edit_desc: Public type used by `save_edit_api`. */
typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    const char *save_path;
} dom_save_edit_desc;

/* Purpose: Open save edit.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dom_save_edit_ctx *dom_save_edit_open(const dom_save_edit_desc *desc);
/* Purpose: Close save edit.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void               dom_save_edit_close(dom_save_edit_ctx *ctx);

/* simple generic key-value editing for now */
int dom_save_edit_list_keys(dom_save_edit_ctx *ctx,
                            const char *section,
                            char *buf,
                            uint32_t buf_size);

/* Purpose: Value dom save edit get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_save_edit_get_value(dom_save_edit_ctx *ctx,
                            const char *section,
                            const char *key,
                            char *buf,
                            uint32_t buf_size);

/* Purpose: Value dom save edit set.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_save_edit_set_value(dom_save_edit_ctx *ctx,
                            const char *section,
                            const char *key,
                            const char *value);

/* Purpose: Save save edit.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_save_edit_save(dom_save_edit_ctx *ctx);

#ifdef __cplusplus
}
#endif

#endif
