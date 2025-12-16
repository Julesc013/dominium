/*
FILE: include/dominium/world_edit_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / world_edit_api
RESPONSIBILITY: Defines the public contract for `world_edit_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
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
typedef struct dom_world_edit_ctx_t dom_world_edit_ctx;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    const char *world_path; /* path to save/universe/world file(s) */
} dom_world_edit_desc;

dom_world_edit_ctx *dom_world_edit_open(const dom_world_edit_desc *desc);
void                dom_world_edit_close(dom_world_edit_ctx *ctx);

/* basic operations, keep small for now */
int dom_world_edit_get_chunk(dom_world_edit_ctx *ctx,
                             int32_t sx, int32_t sy, int32_t sz,
                             dom_chunk_data *out);

int dom_world_edit_set_chunk(dom_world_edit_ctx *ctx,
                             int32_t sx, int32_t sy, int32_t sz,
                             const dom_chunk_data *in);

int dom_world_edit_save(dom_world_edit_ctx *ctx);

#ifdef __cplusplus
}
#endif

#endif
