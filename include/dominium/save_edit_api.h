#ifndef DOMINIUM_SAVE_EDIT_API_H_INCLUDED
#define DOMINIUM_SAVE_EDIT_API_H_INCLUDED

#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_save_edit_ctx_t dom_save_edit_ctx;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    const char *save_path;
} dom_save_edit_desc;

dom_save_edit_ctx *dom_save_edit_open(const dom_save_edit_desc *desc);
void               dom_save_edit_close(dom_save_edit_ctx *ctx);

/* simple generic key-value editing for now */
int dom_save_edit_list_keys(dom_save_edit_ctx *ctx,
                            const char *section,
                            char *buf,
                            uint32_t buf_size);

int dom_save_edit_get_value(dom_save_edit_ctx *ctx,
                            const char *section,
                            const char *key,
                            char *buf,
                            uint32_t buf_size);

int dom_save_edit_set_value(dom_save_edit_ctx *ctx,
                            const char *section,
                            const char *key,
                            const char *value);

int dom_save_edit_save(dom_save_edit_ctx *ctx);

#ifdef __cplusplus
}
#endif

#endif
