/*
FILE: source/domino/core/core.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/core
RESPONSIBILITY: Implements `core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>
#include "core_internal.h"

static const char* g_packages_table_cols[] = { "id", "name", "version", "kind", "path" };
static const char* g_instances_table_cols[] = { "id", "name", "path", "flags", "pkg_count", "last_played" };
static const char* g_mods_table_cols[] = { "id", "name", "version", "kind", "path" };

static void dom_core_register_tables(dom_core* core)
{
    if (!core) {
        return;
    }

    core->table_count = 0u;
    dom_table__register(core,
                        "packages_table",
                        g_packages_table_cols,
                        (uint32_t)(sizeof(g_packages_table_cols) / sizeof(g_packages_table_cols[0])));
    dom_table__register(core,
                        "instances_table",
                        g_instances_table_cols,
                        (uint32_t)(sizeof(g_instances_table_cols) / sizeof(g_instances_table_cols[0])));
    dom_table__register(core,
                        "mods_table",
                        g_mods_table_cols,
                        (uint32_t)(sizeof(g_mods_table_cols) / sizeof(g_mods_table_cols[0])));
}

static void dom_core_add_view(dom_core* core,
                              const char* id,
                              const char* title,
                              dom_view_kind kind,
                              const char* model_id)
{
    dom_view_desc* desc;

    if (!core || core->view_count >= DOM_MAX_VIEWS) {
        return;
    }

    desc = &core->views[core->view_count];
    desc->struct_size = sizeof(dom_view_desc);
    desc->struct_version = 1;
    desc->id = id;
    desc->title = title;
    desc->kind = kind;
    desc->model_id = model_id;
    core->view_count += 1u;
}

static void dom_core_register_views(dom_core* core)
{
    if (!core) {
        return;
    }

    core->view_count = 0u;
    dom_core_add_view(core, "view_instances", "Instances", DOM_VIEW_KIND_TABLE, "instances_table");
    dom_core_add_view(core, "view_packages", "Packages", DOM_VIEW_KIND_TABLE, "packages_table");
    dom_core_add_view(core, "view_mods", "Mods", DOM_VIEW_KIND_TABLE, "mods_table");
    dom_core_add_view(core, "view_packages_tree", "Packages Tree", DOM_VIEW_KIND_TREE, "packages_tree");
    dom_core_add_view(core, "view_world_surface", "World Surface", DOM_VIEW_KIND_CANVAS, "world_surface");
    dom_core_add_view(core, "view_world_orbit", "Orbit Map", DOM_VIEW_KIND_CANVAS, "world_orbit");
}

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
    core->tree_models[0] = "packages_tree";
    core->tree_model_count = 1;

    dom_core_register_tables(core);
    dom_core_register_views(core);

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
