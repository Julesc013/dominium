/*
FILE: include/dominium/launcher_edit_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / launcher_edit_api
RESPONSIBILITY: Defines the public contract for `launcher_edit_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_LAUNCHER_EDIT_API_H_INCLUDED
#define DOMINIUM_LAUNCHER_EDIT_API_H_INCLUDED

#include "domino/baseline.h"
#include "dominium/launch_api.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_launcher_edit_ctx: Public type used by `launcher_edit_api`. */
typedef struct dom_launcher_edit_ctx_t dom_launcher_edit_ctx;

/* dom_launcher_edit_desc: Public type used by `launcher_edit_api`. */
typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    const char *config_path; /* launcher config file / dir */
} dom_launcher_edit_desc;

/* Purpose: Open launcher edit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dom_launcher_edit_ctx *dom_launcher_edit_open(const dom_launcher_edit_desc *desc);
/* Purpose: Close launcher edit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void                   dom_launcher_edit_close(dom_launcher_edit_ctx *ctx);

/* manage tabs/views ordering + visibility */
int dom_launcher_edit_list_tabs(dom_launcher_edit_ctx *ctx,
                                char *buf,
                                uint32_t buf_size);

/* Purpose: Tab dom launcher edit add.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_launcher_edit_add_tab(dom_launcher_edit_ctx *ctx,
                              const char *view_id,
                              const char *title,
                              uint32_t index);

/* Purpose: Tab dom launcher edit remove.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_launcher_edit_remove_tab(dom_launcher_edit_ctx *ctx,
                                 const char *view_id);

/* Purpose: Save launcher edit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_launcher_edit_save(dom_launcher_edit_ctx *ctx);

#ifdef __cplusplus
}
#endif

#endif
