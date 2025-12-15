#ifndef DOMINIUM_LAUNCHER_EDIT_API_H_INCLUDED
#define DOMINIUM_LAUNCHER_EDIT_API_H_INCLUDED

#include "domino/baseline.h"
#include "dominium/launch_api.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_launcher_edit_ctx_t dom_launcher_edit_ctx;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    const char *config_path; /* launcher config file / dir */
} dom_launcher_edit_desc;

dom_launcher_edit_ctx *dom_launcher_edit_open(const dom_launcher_edit_desc *desc);
void                   dom_launcher_edit_close(dom_launcher_edit_ctx *ctx);

/* manage tabs/views ordering + visibility */
int dom_launcher_edit_list_tabs(dom_launcher_edit_ctx *ctx,
                                char *buf,
                                uint32_t buf_size);

int dom_launcher_edit_add_tab(dom_launcher_edit_ctx *ctx,
                              const char *view_id,
                              const char *title,
                              uint32_t index);

int dom_launcher_edit_remove_tab(dom_launcher_edit_ctx *ctx,
                                 const char *view_id);

int dom_launcher_edit_save(dom_launcher_edit_ctx *ctx);

#ifdef __cplusplus
}
#endif

#endif
