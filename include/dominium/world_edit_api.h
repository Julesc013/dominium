#ifndef DOMINIUM_WORLD_EDIT_API_H_INCLUDED
#define DOMINIUM_WORLD_EDIT_API_H_INCLUDED

#include <stdint.h>
#include "domino/dworld.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_chunk_data dom_chunk_data; /* forward until full world chunk format is exposed */
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
