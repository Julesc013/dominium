#include <stdio.h>
#include <string.h>

#include "domino/sys.h"
#include "domino/mod.h"
#include "domino/gfx.h"
#include "dominium/product_info.h"
#include "dominium/version.h"

typedef struct modcheck_ctx {
    domino_package_registry* reg;
} modcheck_ctx;

static int dom_parse_arg(const char* arg, const char* key, char* out, size_t cap)
{
    size_t len;
    if (!arg || !key || !out || cap == 0) return 0;
    len = strlen(key);
    if (strncmp(arg, key, len) != 0) return 0;
    strncpy(out, arg + len, cap - 1);
    out[cap - 1] = '\0';
    return 1;
}

static int dom_modcheck_visit(const domino_package_desc* desc, void* user)
{
    modcheck_ctx* ctx = (modcheck_ctx*)user;
    domino_instance_desc inst;
    domino_resolve_error err;

    if (!ctx || !desc) return 0;
    if (desc->kind != DOMINO_PACKAGE_KIND_MOD) return 0;

    memset(&inst, 0, sizeof(inst));
    strncpy(inst.id, desc->id, sizeof(inst.id) - 1);
    strncpy(inst.product_id, DOMINIUM_GAME_ID, sizeof(inst.product_id) - 1);
    dominium_game_get_version(&inst.product_version);
    inst.mod_count = 1;
    strncpy(inst.mods_enabled[0], desc->id, sizeof(inst.mods_enabled[0]) - 1);

    err.message[0] = '\0';
    if (domino_instance_resolve(ctx->reg, &inst, &err) != 0) {
        printf("Mod %s: incompatible (%s)\n", desc->id,
               err.message[0] ? err.message : "unknown reason");
    } else {
        printf("Mod %s: ok\n", desc->id);
    }
    return 0;
}

int main(int argc, char** argv)
{
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    domino_sys_paths paths;
    const char* roots[2];
    unsigned int root_count = 2;
    domino_package_registry* reg = NULL;
    modcheck_ctx ctx;
    char root_override[260];
    int i;
    char platform_value[32];
    char renderer_value[32];

    platform_value[0] = '\0';
    renderer_value[0] = '\0';
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--introspect-json") == 0) {
            dominium_print_product_info_json(dom_get_product_info_tools(), stdout);
            return 0;
        } else if (strncmp(argv[i], "--platform=", 11) == 0) {
            strncpy(platform_value, argv[i] + 11, sizeof(platform_value) - 1);
            platform_value[sizeof(platform_value) - 1] = '\0';
        } else if (strncmp(argv[i], "--renderer=", 11) == 0) {
            strncpy(renderer_value, argv[i] + 11, sizeof(renderer_value) - 1);
            renderer_value[sizeof(renderer_value) - 1] = '\0';
        }
    }

    if (platform_value[0]) {
        if (dom_sys_select_backend(platform_value) != 0) {
            fprintf(stderr, "Unsupported platform backend '%s'\n", platform_value);
            return 1;
        }
    }
    if (renderer_value[0]) {
        if (dom_gfx_select_backend(renderer_value) != 0) {
            fprintf(stderr, "Unsupported renderer backend '%s'\n", renderer_value);
            return 1;
        }
    }

    root_override[0] = '\0';
    for (i = 1; i < argc; ++i) {
        dom_parse_arg(argv[i], "--root=", root_override, sizeof(root_override));
    }

    sdesc.profile_hint = DOMINO_SYS_PROFILE_FULL;
    if (domino_sys_init(&sdesc, &sys) != 0) {
        return 1;
    }
    domino_sys_get_paths(sys, &paths);

    if (root_override[0]) {
        roots[0] = root_override;
        root_count = 1;
    } else {
        roots[0] = paths.data_root;
        roots[1] = paths.user_root;
    }

    reg = domino_package_registry_create();
    if (!reg) {
        domino_sys_shutdown(sys);
        return 1;
    }
    domino_package_registry_set_sys(reg, sys);
    domino_package_registry_scan_roots(reg, roots, root_count);

    ctx.reg = reg;
    domino_package_registry_visit(reg, dom_modcheck_visit, &ctx);

    domino_package_registry_destroy(reg);
    domino_sys_shutdown(sys);
    return 0;
}
