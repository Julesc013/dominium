/*
Client read-only view model implementation.
*/
#include "readonly_view_model.h"

#include <string.h>

void dom_client_ro_view_model_init(dom_client_ro_view_model* model)
{
    if (!model) {
        return;
    }
    memset(model, 0, sizeof(*model));
}

int dom_client_ro_view_model_load(dom_client_ro_view_model* model,
                                  dom_app_readonly_adapter* ro)
{
    if (!model || !ro) {
        return 0;
    }
    model->has_core = 0;
    model->has_tree = 0;
    memset(&model->core_info, 0, sizeof(model->core_info));
    memset(&model->tree_info, 0, sizeof(model->tree_info));

    if (dom_app_ro_get_core_info(ro, &model->core_info) != DOM_APP_RO_OK) {
        return 0;
    }
    model->has_core = 1;

    if (dom_app_ro_get_tree(ro,
                            "packages_tree",
                            model->nodes,
                            DOM_CLIENT_RO_MAX_NODES,
                            &model->tree_info) == DOM_APP_RO_OK) {
        model->has_tree = 1;
    }
    return 1;
}
