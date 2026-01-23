/*
Client read-only view model for observability.
*/
#ifndef DOMINIUM_CLIENT_READONLY_VIEW_MODEL_H
#define DOMINIUM_CLIENT_READONLY_VIEW_MODEL_H

#include "dominium/app/readonly_adapter.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_CLIENT_RO_MAX_NODES 256u

typedef struct dom_client_ro_view_model {
    dom_app_ro_core_info core_info;
    dom_app_ro_tree_info tree_info;
    dom_app_ro_tree_node nodes[DOM_CLIENT_RO_MAX_NODES];
    int has_core;
    int has_tree;
} dom_client_ro_view_model;

void dom_client_ro_view_model_init(dom_client_ro_view_model* model);
int  dom_client_ro_view_model_load(dom_client_ro_view_model* model,
                                   dom_app_readonly_adapter* ro);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CLIENT_READONLY_VIEW_MODEL_H */
