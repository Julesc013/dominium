#include <stdlib.h>
#include <string.h>
#include "core_internal.h"

dom_core* dom_core_create(const dom_core_desc* desc)
{
    dom_core* core;

    core = (dom_core*)malloc(sizeof(dom_core));
    if (!core) {
        return NULL;
    }
    memset(core, 0, sizeof(*core));

    if (desc) {
        core->api_version = desc->api_version;
    }

    core->next_package_id = 1;
    core->next_instance_id = 1;
    core->table_models[0] = "instances_table";
    core->table_model_count = 1;
    core->tree_models[0] = "empty_tree";
    core->tree_model_count = 1;

    /* default view for the instances table */
    core->views[0].struct_size = sizeof(dom_view_desc);
    core->views[0].struct_version = 1;
    core->views[0].id = "instances_view";
    core->views[0].title = "Instances";
    core->views[0].kind = DOM_VIEW_KIND_TABLE;
    core->views[0].model_id = "instances_table";
    core->view_count = 1;

    return core;
}

void dom_core_destroy(dom_core* core)
{
    if (!core) {
        return;
    }
    free(core);
}

bool dom_core_execute(dom_core* core, const dom_cmd* cmd)
{
    if (!core || !cmd) {
        return false;
    }

    switch (cmd->id) {
    case DOM_CMD_NOP:
        return true;
    default:
        break;
    }

    return false;
}

bool dom_core_query(dom_core* core, dom_query* q)
{
    dom_core_info info;

    if (!core || !q) {
        return false;
    }

    switch (q->id) {
    case DOM_QUERY_CORE_INFO:
        if (!q->out || q->out_size < sizeof(dom_core_info)) {
            return false;
        }
        info.struct_size = sizeof(dom_core_info);
        info.struct_version = 1;
        info.api_version = core->api_version;
        info.package_count = core->package_count;
        info.instance_count = core->instance_count;
        info.ticks = core->tick_counter;
        memcpy(q->out, &info, sizeof(info));
        return true;
    default:
        break;
    }

    return false;
}
