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

    dom_core__scan_packages(core);
    dom_core__scan_instances(core);

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
    const dom_cmd_pkg_install*  c_pkg_install;
    const dom_cmd_pkg_uninstall* c_pkg_uninstall;
    const dom_cmd_inst_create*  c_inst_create;
    const dom_cmd_inst_update*  c_inst_update;
    const dom_cmd_inst_delete*  c_inst_delete;
    const dom_cmd_sim_tick*     c_sim_tick;
    dom_event                   ev;
    dom_package_id              pkg_id;
    dom_instance_id             inst_id;

    if (!core || !cmd) {
        return false;
    }

    switch (cmd->id) {
    case DOM_CMD_NOP:
        return true;
    case DOM_CMD_PKG_INSTALL:
        if (!cmd->data || cmd->size < sizeof(dom_cmd_pkg_install)) {
            return false;
        }
        c_pkg_install = (const dom_cmd_pkg_install*)cmd->data;
        if (!dom_pkg_install(core, c_pkg_install->source_path, &pkg_id)) {
            return false;
        }
        ev.struct_size = sizeof(dom_event);
        ev.struct_version = 1;
        ev.kind = DOM_EVT_PKG_INSTALLED;
        ev.u.pkg_id = pkg_id;
        dom_event__publish(core, &ev);
        return true;
    case DOM_CMD_PKG_UNINSTALL:
        if (!cmd->data || cmd->size < sizeof(dom_cmd_pkg_uninstall)) {
            return false;
        }
        c_pkg_uninstall = (const dom_cmd_pkg_uninstall*)cmd->data;
        if (!dom_pkg_uninstall(core, c_pkg_uninstall->id)) {
            return false;
        }
        ev.struct_size = sizeof(dom_event);
        ev.struct_version = 1;
        ev.kind = DOM_EVT_PKG_UNINSTALLED;
        ev.u.pkg_id = c_pkg_uninstall->id;
        dom_event__publish(core, &ev);
        return true;
    case DOM_CMD_INST_CREATE:
        if (!cmd->data || cmd->size < sizeof(dom_cmd_inst_create)) {
            return false;
        }
        c_inst_create = (const dom_cmd_inst_create*)cmd->data;
        if (c_inst_create->info.struct_size != sizeof(dom_instance_info) ||
            c_inst_create->info.struct_version != 1) {
            return false;
        }
        inst_id = dom_inst_create(core, &c_inst_create->info);
        if (inst_id == 0) {
            return false;
        }
        ev.struct_size = sizeof(dom_event);
        ev.struct_version = 1;
        ev.kind = DOM_EVT_INST_CREATED;
        ev.u.inst_id = inst_id;
        dom_event__publish(core, &ev);
        return true;
    case DOM_CMD_INST_UPDATE:
        if (!cmd->data || cmd->size < sizeof(dom_cmd_inst_update)) {
            return false;
        }
        c_inst_update = (const dom_cmd_inst_update*)cmd->data;
        if (c_inst_update->info.struct_size != sizeof(dom_instance_info) ||
            c_inst_update->info.struct_version != 1) {
            return false;
        }
        if (!dom_inst_update(core, &c_inst_update->info)) {
            return false;
        }
        ev.struct_size = sizeof(dom_event);
        ev.struct_version = 1;
        ev.kind = DOM_EVT_INST_UPDATED;
        ev.u.inst_id = c_inst_update->info.id;
        dom_event__publish(core, &ev);
        return true;
    case DOM_CMD_INST_DELETE:
        if (!cmd->data || cmd->size < sizeof(dom_cmd_inst_delete)) {
            return false;
        }
        c_inst_delete = (const dom_cmd_inst_delete*)cmd->data;
        if (!dom_inst_delete(core, c_inst_delete->id)) {
            return false;
        }
        ev.struct_size = sizeof(dom_event);
        ev.struct_version = 1;
        ev.kind = DOM_EVT_INST_DELETED;
        ev.u.inst_id = c_inst_delete->id;
        dom_event__publish(core, &ev);
        return true;
    case DOM_CMD_SIM_TICK:
        if (!cmd->data || cmd->size < sizeof(dom_cmd_sim_tick)) {
            return false;
        }
        c_sim_tick = (const dom_cmd_sim_tick*)cmd->data;
        return dom_sim_tick(core, c_sim_tick->id, c_sim_tick->ticks);
    default:
        break;
    }

    return false;
}

bool dom_core_query(dom_core* core, dom_query* q)
{
    dom_query_core_info_out* core_out;
    dom_query_pkg_list_out*  pkg_list_out;
    dom_query_pkg_info_in*   pkg_info_in;
    dom_query_pkg_info_out*  pkg_info_out;
    dom_query_inst_list_out* inst_list_out;
    dom_query_inst_info_in*  inst_info_in;
    dom_query_inst_info_out* inst_info_out;
    dom_query_sim_state_in*  sim_in;
    dom_query_sim_state_out* sim_out;

    if (!core || !q) {
        return false;
    }

    switch (q->id) {
    case DOM_QUERY_CORE_INFO:
        if (!q->out || q->out_size < sizeof(dom_query_core_info_out)) {
            return false;
        }
        core_out = (dom_query_core_info_out*)q->out;
        core_out->struct_size = sizeof(dom_query_core_info_out);
        core_out->struct_version = 1;
        core_out->api_version = core->api_version;
        core_out->package_count = core->package_count;
        core_out->instance_count = core->instance_count;
        return true;
    case DOM_QUERY_PKG_LIST:
        if (!q->out || q->out_size < sizeof(dom_query_pkg_list_out)) {
            return false;
        }
        pkg_list_out = (dom_query_pkg_list_out*)q->out;
        if (!pkg_list_out->items || pkg_list_out->max_items == 0) {
            return false;
        }
        pkg_list_out->count = dom_pkg_list(core,
                                           pkg_list_out->items,
                                           pkg_list_out->max_items);
        return true;
    case DOM_QUERY_PKG_INFO:
        if (!q->in || q->in_size < sizeof(dom_query_pkg_info_in) ||
            !q->out || q->out_size < sizeof(dom_query_pkg_info_out)) {
            return false;
        }
        pkg_info_in = (dom_query_pkg_info_in*)q->in;
        pkg_info_out = (dom_query_pkg_info_out*)q->out;
        if (!dom_pkg_get(core, pkg_info_in->id, &pkg_info_out->info)) {
            return false;
        }
        pkg_info_out->id = pkg_info_in->id;
        return true;
    case DOM_QUERY_INST_LIST:
        if (!q->out || q->out_size < sizeof(dom_query_inst_list_out)) {
            return false;
        }
        inst_list_out = (dom_query_inst_list_out*)q->out;
        if (!inst_list_out->items || inst_list_out->max_items == 0) {
            return false;
        }
        inst_list_out->count = dom_inst_list(core,
                                             inst_list_out->items,
                                             inst_list_out->max_items);
        return true;
    case DOM_QUERY_INST_INFO:
        if (!q->in || q->in_size < sizeof(dom_query_inst_info_in) ||
            !q->out || q->out_size < sizeof(dom_query_inst_info_out)) {
            return false;
        }
        inst_info_in = (dom_query_inst_info_in*)q->in;
        inst_info_out = (dom_query_inst_info_out*)q->out;
        if (!dom_inst_get(core, inst_info_in->id, &inst_info_out->info)) {
            return false;
        }
        inst_info_out->id = inst_info_in->id;
        return true;
    case DOM_QUERY_SIM_STATE:
        if (!q->in || q->in_size < sizeof(dom_query_sim_state_in) ||
            !q->out || q->out_size < sizeof(dom_query_sim_state_out)) {
            return false;
        }
        sim_in = (dom_query_sim_state_in*)q->in;
        sim_out = (dom_query_sim_state_out*)q->out;
        if (!dom_sim_get_state(core, sim_in->id, &sim_out->state)) {
            return false;
        }
        sim_out->id = sim_in->id;
        return true;
    default:
        break;
    }

    return false;
}
