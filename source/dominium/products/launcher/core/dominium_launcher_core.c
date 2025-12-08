#include "dominium_launcher_core.h"
#include "domino/sys.h"
#include "domino/mod.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dominium_launcher_view_registry.h"
#include "dominium_launcher_instances.h"

struct dominium_launcher_context {
    domino_sys_context*          sys;
    domino_sys_paths             paths;

    domino_package_registry*     registry;

    /* Loaded instances cache */
    domino_instance_desc*        instances;
    unsigned int                 instance_count;
    unsigned int                 instance_capacity;

    /* View registry */
    dominium_launcher_view_registry* view_registry;

    /* Services: start with instances service */
    dominium_launcher_instances_service* instances_service;
};

static void dom_join(char* dst, size_t cap,
                     const char* a, const char* b)
{
    size_t i = 0;
    size_t j = 0;
    if (!dst || cap == 0) return;
    if (!a) a = "";
    if (!b) b = "";
    while (a[i] != '\0' && i + 1 < cap) {
        dst[i] = a[i];
        ++i;
    }
    if (i > 0 && i + 1 < cap) {
        char c = dst[i - 1];
        if (c != '/' && c != '\\') {
            dst[i++] = '/';
        }
    }
    while (b[j] != '\0' && i + 1 < cap) {
        dst[i++] = b[j++];
    }
    dst[i] = '\0';
}

static int dom_has_suffix(const char* name, const char* suffix)
{
    size_t nlen, slen;
    if (!name || !suffix) return 0;
    nlen = strlen(name);
    slen = strlen(suffix);
    if (nlen < slen) return 0;
    return (strcmp(name + (nlen - slen), suffix) == 0);
}

static int dominium_launcher_ensure_instance_capacity(dominium_launcher_context* ctx,
                                                      unsigned int needed)
{
    domino_instance_desc* new_arr;
    unsigned int new_cap;
    if (needed <= ctx->instance_capacity) return 0;
    new_cap = ctx->instance_capacity ? ctx->instance_capacity * 2 : 8;
    while (new_cap < needed) {
        new_cap *= 2;
    }
    new_arr = (domino_instance_desc*)realloc(ctx->instances,
                                             new_cap * sizeof(domino_instance_desc));
    if (!new_arr) return -1;
    ctx->instances = new_arr;
    ctx->instance_capacity = new_cap;
    return 0;
}

static int dominium_launcher_add_instance(dominium_launcher_context* ctx,
                                          const char* path)
{
    domino_instance_desc inst;
    if (!ctx || !path) return -1;
    if (domino_instance_load(path, &inst) != 0) return -1;
    strncpy(inst.root_path, path, sizeof(inst.root_path) - 1);
    inst.root_path[sizeof(inst.root_path) - 1] = '\0';
    if (dominium_launcher_ensure_instance_capacity(ctx, ctx->instance_count + 1) != 0) {
        return -1;
    }
    ctx->instances[ctx->instance_count++] = inst;
    return 0;
}

int dominium_launcher_init(dominium_launcher_context** out_ctx)
{
    dominium_launcher_context* ctx;
    domino_sys_desc sdesc;
    if (!out_ctx) return -1;
    *out_ctx = NULL;

    ctx = (dominium_launcher_context*)malloc(sizeof(dominium_launcher_context));
    if (!ctx) return -1;
    memset(ctx, 0, sizeof(*ctx));

    sdesc.profile_hint = DOMINO_SYS_PROFILE_FULL;
    if (domino_sys_init(&sdesc, &ctx->sys) != 0) {
        dominium_launcher_shutdown(ctx);
        return -1;
    }
    domino_sys_get_paths(ctx->sys, &ctx->paths);

    ctx->registry = domino_package_registry_create();
    if (!ctx->registry) {
        dominium_launcher_shutdown(ctx);
        return -1;
    }
    domino_package_registry_set_sys(ctx->registry, ctx->sys);

    ctx->view_registry = dominium_launcher_view_registry_create();
    if (!ctx->view_registry) {
        dominium_launcher_shutdown(ctx);
        return -1;
    }

    ctx->instances_service = NULL;
    if (dominium_launcher_instances_create(ctx, &ctx->instances_service) != 0) {
        dominium_launcher_shutdown(ctx);
        return -1;
    }

    if (dominium_launcher_reload_registry(ctx) != 0) {
        dominium_launcher_shutdown(ctx);
        return -1;
    }
    if (dominium_launcher_reload_instances(ctx) != 0) {
        dominium_launcher_shutdown(ctx);
        return -1;
    }

    if (dominium_launcher_instances_register_views(ctx->instances_service, ctx->view_registry) != 0) {
        domino_sys_log(ctx->sys,
                       DOMINO_LOG_WARN,
                       "launcher",
                       "Failed to register built-in launcher views");
    }

    *out_ctx = ctx;
    return 0;
}

void dominium_launcher_shutdown(dominium_launcher_context* ctx)
{
    if (!ctx) return;

    if (ctx->instances_service) {
        dominium_launcher_instances_destroy(ctx->instances_service);
    }

    if (ctx->view_registry) {
        dominium_launcher_view_registry_destroy(ctx->view_registry);
    }

    if (ctx->instances) {
        free(ctx->instances);
    }

    if (ctx->registry) {
        domino_package_registry_destroy(ctx->registry);
    }

    if (ctx->sys) {
        domino_sys_shutdown(ctx->sys);
    }

    free(ctx);
}

int dominium_launcher_reload_registry(dominium_launcher_context* ctx)
{
    domino_package_registry* new_reg;
    const char* roots[2];
    if (!ctx || !ctx->sys) return -1;

    new_reg = domino_package_registry_create();
    if (!new_reg) return -1;
    domino_package_registry_set_sys(new_reg, ctx->sys);

    roots[0] = ctx->paths.data_root;
    roots[1] = ctx->paths.user_root;

    if (domino_package_registry_scan_roots(new_reg, roots, 2) != 0) {
        domino_package_registry_destroy(new_reg);
        return -1;
    }

    if (ctx->registry) {
        domino_package_registry_destroy(ctx->registry);
    }
    ctx->registry = new_reg;
    return 0;
}

int dominium_launcher_reload_instances(dominium_launcher_context* ctx)
{
    domino_sys_dir_iter* it;
    char inst_root[260];
    char name[260];
    int is_dir = 0;

    if (!ctx || !ctx->sys) return -1;

    ctx->instance_count = 0;
    dom_join(inst_root, sizeof(inst_root), ctx->paths.state_root, "instances");
    domino_sys_mkdirs(ctx->sys, inst_root);

    it = domino_sys_dir_open(ctx->sys, inst_root);
    if (!it) {
        if (ctx->instances_service) {
            dominium_launcher_instances_reload(ctx->instances_service);
        }
        return 0;
    }

    while (domino_sys_dir_next(ctx->sys, it, name, sizeof(name), &is_dir)) {
        char candidate[260];
        if (name[0] == '.') continue;
        if (is_dir) {
            dom_join(candidate, sizeof(candidate), inst_root, name);
            dom_join(candidate, sizeof(candidate), candidate, "instance.toml");
            dominium_launcher_add_instance(ctx, candidate);
        } else if (dom_has_suffix(name, ".instance.toml")) {
            dom_join(candidate, sizeof(candidate), inst_root, name);
            dominium_launcher_add_instance(ctx, candidate);
        }
    }
    domino_sys_dir_close(ctx->sys, it);

    if (ctx->instances_service) {
        dominium_launcher_instances_reload(ctx->instances_service);
    }
    return 0;
}

domino_sys_context* dominium_launcher_get_sys(dominium_launcher_context* ctx)
{
    return ctx ? ctx->sys : NULL;
}

const domino_package_registry* dominium_launcher_get_registry(dominium_launcher_context* ctx)
{
    return ctx ? ctx->registry : NULL;
}

dominium_launcher_view_registry* dominium_launcher_get_view_registry(dominium_launcher_context* ctx)
{
    return ctx ? ctx->view_registry : NULL;
}

int dominium_launcher_list_instances(dominium_launcher_context* ctx,
                                     domino_instance_desc* out,
                                     unsigned int max_count,
                                     unsigned int* out_count)
{
    unsigned int i;
    unsigned int copy = 0;
    if (!ctx) return -1;
    if (out && max_count > 0) {
        copy = (ctx->instance_count < max_count) ? ctx->instance_count : max_count;
        for (i = 0; i < copy; ++i) {
            out[i] = ctx->instances[i];
        }
    }
    if (out_count) *out_count = ctx->instance_count;
    return 0;
}

int dominium_launcher_resolve_instance(dominium_launcher_context* ctx,
                                       const domino_instance_desc* inst,
                                       domino_resolve_error* err)
{
    if (!ctx || !ctx->registry) return -1;
    return domino_instance_resolve(ctx->registry, inst, err);
}

static void dom_format_version(const domino_semver* v,
                               char* out, size_t cap)
{
    if (!v || !out || cap == 0) return;
    sprintf(out, "%d.%d.%d", v->major, v->minor, v->patch);
    out[cap - 1] = '\0';
}

int dominium_launcher_run_instance(dominium_launcher_context* ctx,
                                   const char* instance_id)
{
    unsigned int i;
    char exe_path[260];
    const char* argv_run[3];
    char arg_instance[280];
    domino_sys_process_desc pdesc;
    domino_sys_process* proc = NULL;
    int exit_code = 0;
    domino_resolve_error err;

    if (!ctx || !instance_id) return -1;

    for (i = 0; i < ctx->instance_count; ++i) {
        domino_instance_desc* inst = &ctx->instances[i];
        if (strcmp(inst->id, instance_id) != 0) continue;

        err.message[0] = '\0';
        if (domino_instance_resolve(ctx->registry, inst, &err) != 0) {
            if (err.message[0]) {
                domino_sys_log(ctx->sys, DOMINO_LOG_ERROR, "launcher", err.message);
            }
            return -1;
        }

        /* TODO: refine binary resolution using product manifests and per-platform binaries */
#if defined(_WIN32)
        dom_join(exe_path, sizeof(exe_path), ctx->paths.program_root, "dominium_game_cli.exe");
#else
        dom_join(exe_path, sizeof(exe_path), ctx->paths.program_root, "dominium_game_cli");
#endif

        strncpy(arg_instance, "--instance=", sizeof(arg_instance) - 1);
        arg_instance[sizeof(arg_instance) - 1] = '\0';
        strncat(arg_instance, inst->root_path, sizeof(arg_instance) - strlen(arg_instance) - 1);

        argv_run[0] = exe_path;
        argv_run[1] = arg_instance;
        argv_run[2] = NULL;

        memset(&pdesc, 0, sizeof(pdesc));
        pdesc.path = exe_path;
        pdesc.argv = argv_run;
        pdesc.working_dir = NULL;

        if (domino_sys_process_spawn(ctx->sys, &pdesc, &proc) != 0) {
            domino_sys_log(ctx->sys, DOMINO_LOG_ERROR, "launcher", "Failed to spawn game");
            return -1;
        }
        domino_sys_process_wait(ctx->sys, proc, &exit_code);
        domino_sys_process_destroy(ctx->sys, proc);
        return exit_code;
    }

    domino_sys_log(ctx->sys, DOMINO_LOG_WARN, "launcher", "Instance not found");
    return -1;
}
