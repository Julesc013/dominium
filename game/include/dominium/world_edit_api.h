/*
FILE: include/dominium/world_edit_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / world_edit_api
RESPONSIBILITY: Defines the public contract for `world_edit_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_WORLD_EDIT_API_H_INCLUDED
#define DOMINIUM_WORLD_EDIT_API_H_INCLUDED

#include "domino/baseline.h"
#include "domino/dworld.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Temporary placeholder until real chunk format is wired */
typedef struct dom_chunk_data {
    uint8_t bytes[1];
} dom_chunk_data;
/* dom_world_edit_ctx: Public type used by `world_edit_api`. */
typedef struct dom_world_edit_ctx_t dom_world_edit_ctx;

/* dom_world_edit_desc: Public type used by `world_edit_api`. */
typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    const char *world_path; /* path to save/universe/world file(s) */
} dom_world_edit_desc;

/* Purpose: Open world edit.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dom_world_edit_ctx *dom_world_edit_open(const dom_world_edit_desc *desc);
/* Purpose: Close world edit.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void                dom_world_edit_close(dom_world_edit_ctx *ctx);

/* basic operations, keep small for now */
int dom_world_edit_get_chunk(dom_world_edit_ctx *ctx,
                             int32_t sx, int32_t sy, int32_t sz,
                             dom_chunk_data *out);

/* Purpose: Chunk dom world edit set.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_world_edit_set_chunk(dom_world_edit_ctx *ctx,
                             int32_t sx, int32_t sy, int32_t sz,
                             const dom_chunk_data *in);

/* Purpose: Save world edit.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_world_edit_save(dom_world_edit_ctx *ctx);

#ifdef __cplusplus
}
#endif

#endif
