#include "dominium/launch_api.h"

#include <stdlib.h>
#include <string.h>

#include "domino/inst.h"
#include "domino/pkg.h"
#include "domino/sys.h"

struct dom_launch_ctx_t {
    dom_core        *core;
    dom_launch_desc  desc;
    dom_launch_state state;
    dom_instance_id  current_instance;
    dom_package_id   current_package;
    const char      *current_view_id;
};

static void dom_launch_copy_string(char* dst, size_t cap, const char* src)
{
    size_t i;
    if (!dst || cap == 0u) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }
    for (i = 0u; i + 1u < cap && src[i] != '\0'; ++i) {
        dst[i] = src[i];
    }
    dst[i] = '\0';
}

static const char* dom_launch_select_view(dom_launch_ctx* ctx, const char* preferred)
{
    dom_view_desc views[8];
    uint32_t      count;
    uint32_t      i;

    if (!ctx || !ctx->core) {
        return preferred;
    }

    memset(views, 0, sizeof(views));
    count = dom_ui_list_views(ctx->core, views, (uint32_t)(sizeof(views) / sizeof(views[0])));
    if (count == 0u) {
        return preferred;
    }

    if (preferred) {
        for (i = 0u; i < count; ++i) {
            if (views[i].id && strcmp(views[i].id, preferred) == 0) {
                return views[i].id;
            }
        }
    }

    return views[0].id;
}

static void dom_launch_attach_default_packages(dom_launch_ctx* ctx,
                                               dom_instance_info* info)
{
    dom_package_info pkg_buf[DOM_MAX_INSTANCE_PACKAGES];
    uint32_t         pkg_count;
    uint32_t         attached;
    uint32_t         i;

    if (!ctx || !info) {
        return;
    }

    memset(pkg_buf, 0, sizeof(pkg_buf));
    pkg_count = dom_pkg_list(ctx->core, pkg_buf, (uint32_t)(sizeof(pkg_buf) / sizeof(pkg_buf[0])));

    attached = 0u;
    for (i = 0u; i < pkg_count && attached < DOM_MAX_INSTANCE_PACKAGES; ++i) {
        if (pkg_buf[i].kind == DOM_PKG_KIND_PRODUCT ||
            pkg_buf[i].kind == DOM_PKG_KIND_CONTENT ||
            pkg_buf[i].kind == DOM_PKG_KIND_PACK) {
            info->pkgs[attached] = pkg_buf[i].id;
            attached += 1u;
            if (pkg_buf[i].kind == DOM_PKG_KIND_PRODUCT) {
                break;
            }
        }
    }

    if (attached == 0u && pkg_count > 0u) {
        info->pkgs[0] = pkg_buf[0].id;
        attached = 1u;
    }

    info->pkg_count = attached;
}

static dom_instance_id dom_launch_create_instance(dom_launch_ctx* ctx, const char* name_hint)
{
    dom_instance_info info;
    const char*       name;

    if (!ctx || !ctx->core) {
        return 0u;
    }

    memset(&info, 0, sizeof(info));
    info.struct_size = sizeof(info);
    info.struct_version = 1;

    name = name_hint;
    if (!name || name[0] == '\0') {
        name = "New Instance";
    }
    dom_launch_copy_string(info.name, sizeof(info.name), name);

    dom_launch_attach_default_packages(ctx, &info);

    return dom_inst_create(ctx->core, &info);
}

dom_launch_ctx* dom_launch_create(const dom_launch_desc* desc)
{
    dom_launch_ctx* ctx;

    if (!desc || desc->struct_size < sizeof(dom_launch_desc) || !desc->core) {
        return NULL;
    }

    ctx = (dom_launch_ctx*)malloc(sizeof(dom_launch_ctx));
    if (!ctx) {
        return NULL;
    }

    memset(ctx, 0, sizeof(*ctx));
    ctx->core = desc->core;
    ctx->desc = *desc;
    ctx->state = DOM_LAUNCH_STATE_MAIN;
    ctx->current_view_id = dom_launch_select_view(ctx, "view_instances");
    if (!ctx->current_view_id) {
        ctx->current_view_id = "view_instances";
    }

    return ctx;
}

void dom_launch_destroy(dom_launch_ctx* ctx)
{
    if (!ctx) {
        return;
    }
    free(ctx);
}

void dom_launch_get_snapshot(dom_launch_ctx* ctx, dom_launch_snapshot* out)
{
    if (!ctx || !out) {
        return;
    }

    memset(out, 0, sizeof(*out));
    out->struct_size = sizeof(dom_launch_snapshot);
    out->struct_version = 1;
    out->state = ctx->state;
    out->current_instance = ctx->current_instance;
    out->current_package = ctx->current_package;
    out->current_view_id = ctx->current_view_id;
}

uint32_t dom_launch_list_views(dom_launch_ctx* ctx, dom_view_desc* out, uint32_t max_out)
{
    if (!ctx) {
        return 0u;
    }
    return dom_ui_list_views(ctx->core, out, max_out);
}

void dom_launch_handle_action(dom_launch_ctx* ctx,
                              dom_launch_action action,
                              uint32_t param_u32,
                              const char* param_str)
{
    dom_instance_id created;
    const char*     view_id;

    if (!ctx) {
        return;
    }

    created = 0u;
    view_id = NULL;

    switch (action) {
    case DOM_LAUNCH_ACTION_QUIT:
        ctx->state = DOM_LAUNCH_STATE_STARTUP;
        break;

    case DOM_LAUNCH_ACTION_LIST_INSTANCES:
        ctx->state = DOM_LAUNCH_STATE_INSTANCE_MANAGER;
        ctx->current_view_id = dom_launch_select_view(ctx, "view_instances");
        break;

    case DOM_LAUNCH_ACTION_CREATE_INSTANCE:
        created = dom_launch_create_instance(ctx, param_str);
        if (created != 0u) {
            ctx->current_instance = created;
            ctx->state = DOM_LAUNCH_STATE_INSTANCE_MANAGER;
        }
        break;

    case DOM_LAUNCH_ACTION_EDIT_INSTANCE:
        ctx->current_instance = param_u32;
        ctx->state = DOM_LAUNCH_STATE_INSTANCE_MANAGER;
        break;

    case DOM_LAUNCH_ACTION_DELETE_INSTANCE:
        if (param_u32 != 0u) {
            dom_inst_delete(ctx->core, param_u32);
            if (ctx->current_instance == param_u32) {
                ctx->current_instance = 0u;
            }
        }
        break;

    case DOM_LAUNCH_ACTION_LAUNCH_INSTANCE:
        if (dom_launch_run_instance(ctx, param_u32) == 0) {
            ctx->state = DOM_LAUNCH_STATE_RUNNING_INSTANCE;
            ctx->current_instance = param_u32;
        }
        break;

    case DOM_LAUNCH_ACTION_LIST_PACKAGES:
        ctx->state = DOM_LAUNCH_STATE_PACKAGE_MANAGER;
        view_id = dom_launch_select_view(ctx, "view_packages");
        if (!view_id) {
            view_id = dom_launch_select_view(ctx, "view_mods");
        }
        ctx->current_view_id = view_id;
        break;

    case DOM_LAUNCH_ACTION_ENABLE_MOD:
    case DOM_LAUNCH_ACTION_DISABLE_MOD:
        ctx->current_package = param_u32;
        break;

    case DOM_LAUNCH_ACTION_OPEN_SETTINGS:
        ctx->state = DOM_LAUNCH_STATE_SETTINGS;
        ctx->current_view_id = dom_launch_select_view(ctx, "view_settings");
        break;

    case DOM_LAUNCH_ACTION_VIEW_WORLD:
        view_id = param_str && param_str[0] ? param_str : "view_world_surface";
        ctx->current_view_id = dom_launch_select_view(ctx, view_id);
        ctx->state = DOM_LAUNCH_STATE_MAIN;
        break;

    case DOM_LAUNCH_ACTION_NONE:
    default:
        break;
    }
}

int dom_launch_run_instance(dom_launch_ctx* ctx, dom_instance_id inst_id)
{
    dsys_process_desc pdesc;
    const char*       argv_local[2];
    dsys_process*     proc;
    dom_instance_info info;

    if (!ctx || !ctx->core || inst_id == 0u) {
        return -1;
    }

    memset(&info, 0, sizeof(info));
    if (!dom_inst_get(ctx->core, inst_id, &info)) {
        return -1;
    }

    memset(&pdesc, 0, sizeof(pdesc));
    pdesc.exe = info.path;
    if (!pdesc.exe || pdesc.exe[0] == '\0') {
        if (ctx->desc.product_id && ctx->desc.product_id[0] != '\0') {
            pdesc.exe = ctx->desc.product_id;
        } else {
            pdesc.exe = "dominium_game_cli";
        }
    }

    argv_local[0] = pdesc.exe;
    argv_local[1] = NULL;
    pdesc.argv = argv_local;

    proc = dsys_process_spawn(&pdesc);
    if (!proc) {
        return -1;
    }

    dsys_process_destroy(proc);
    return 0;
}
