#include "dominium_launcher_instances.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dominium_launcher_core.h"
#include "domino/sys.h"
#include "domino/mod.h"
#include "dominium_launcher_view.h"

struct dominium_launcher_instances_service {
    dominium_launcher_context* lctx;
};

static int instances_view_render_cli(dominium_launcher_context* lctx,
                                     struct dominium_launcher_view* view,
                                     struct dominium_launcher_view_cli_ctx* cli)
{
    domino_instance_desc inst_buf[128];
    unsigned int count = 0;
    unsigned int i;
    (void)view;
    (void)cli;

    if (dominium_launcher_list_instances(lctx, inst_buf, 128, &count) != 0) {
        printf("Failed to list instances.\n");
        return 1;
    }

    printf("Instances:\n");
    if (count == 0) {
        printf("  (none found)\n");
        return 0;
    }

    for (i = 0; i < count; ++i) {
        printf("  %s [%s %d.%d.%d] mods=%u packs=%u\n",
               inst_buf[i].id,
               inst_buf[i].product_id,
               inst_buf[i].product_version.major,
               inst_buf[i].product_version.minor,
               inst_buf[i].product_version.patch,
               inst_buf[i].mod_count,
               inst_buf[i].pack_count);
    }

    return 0;
}

int dominium_launcher_instances_create(dominium_launcher_context* lctx,
                                       dominium_launcher_instances_service** out_svc)
{
    dominium_launcher_instances_service* svc;
    if (!out_svc) return -1;
    *out_svc = NULL;
    svc = (dominium_launcher_instances_service*)malloc(sizeof(dominium_launcher_instances_service));
    if (!svc) return -1;
    svc->lctx = lctx;
    *out_svc = svc;
    return 0;
}

void dominium_launcher_instances_destroy(dominium_launcher_instances_service* svc)
{
    if (!svc) return;
    free(svc);
}

int dominium_launcher_instances_reload(dominium_launcher_instances_service* svc)
{
    (void)svc;
    /* Instances are currently cached on the launcher context; service can add indexing later. */
    return 0;
}

int dominium_launcher_instances_create_instance(dominium_launcher_instances_service* svc,
                                                const domino_instance_desc* tmpl)
{
    (void)tmpl;
    if (!svc) return -1;
    /* TODO: write new instance file into state_root/instances and trigger reload. */
    domino_sys_log(dominium_launcher_get_sys(svc->lctx),
                   DOMINO_LOG_WARN,
                   "launcher.instances",
                   "create_instance is not implemented yet");
    return -1;
}

int dominium_launcher_instances_delete_instance(dominium_launcher_instances_service* svc,
                                                const char* id)
{
    (void)id;
    if (!svc) return -1;
    /* TODO: delete instance file from state_root/instances and trigger reload. */
    domino_sys_log(dominium_launcher_get_sys(svc->lctx),
                   DOMINO_LOG_WARN,
                   "launcher.instances",
                   "delete_instance is not implemented yet");
    return -1;
}

int dominium_launcher_instances_register_views(dominium_launcher_instances_service* svc,
                                               dominium_launcher_view_registry* vreg)
{
    dominium_launcher_view_desc desc;
    if (!svc || !vreg) return -1;
    memset(&desc, 0, sizeof(desc));
    strncpy(desc.id, "instances", sizeof(desc.id) - 1);
    strncpy(desc.label, "Instances", sizeof(desc.label) - 1);
    desc.kind = DOMINIUM_VIEW_KIND_LIST;
    desc.source = DOMINIUM_VIEW_SOURCE_BUILTIN;
    desc.priority = 100;
    desc.render_cli = instances_view_render_cli;
    desc.render_tui = NULL;
    desc.render_gui = NULL;
    desc.script_entry[0] = '\0';
    desc.user_data = svc;
    return dominium_launcher_view_register(vreg, &desc);
}
