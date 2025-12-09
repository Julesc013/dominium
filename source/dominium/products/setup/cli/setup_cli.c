#include <stdio.h>
#include <string.h>

#include "domino/sys.h"
#include "domino/core.h"
#include "dominium/version.h"
#include "dominium/setup_api.h"

static void dom_setup_cli_print_usage(void)
{
    printf("Usage: dominium-setup-cli --scope=portable|user|system "
           "--action=install|repair|uninstall|verify [--dir=<path>] [--quiet]\n");
}

static int dom_setup_cli_parse_scope(const char* value, dom_setup_scope* out)
{
    if (!value || !out) {
        return 0;
    }
    if (strcmp(value, "portable") == 0) {
        *out = DOM_SETUP_SCOPE_PORTABLE;
        return 1;
    }
    if (strcmp(value, "user") == 0 || strcmp(value, "per-user") == 0) {
        *out = DOM_SETUP_SCOPE_PER_USER;
        return 1;
    }
    if (strcmp(value, "system") == 0 || strcmp(value, "all-users") == 0) {
        *out = DOM_SETUP_SCOPE_ALL_USERS;
        return 1;
    }
    return 0;
}

static int dom_setup_cli_parse_action(const char* value, dom_setup_action* out)
{
    if (!value || !out) {
        return 0;
    }
    if (strcmp(value, "install") == 0) {
        *out = DOM_SETUP_ACTION_INSTALL;
        return 1;
    }
    if (strcmp(value, "repair") == 0) {
        *out = DOM_SETUP_ACTION_REPAIR;
        return 1;
    }
    if (strcmp(value, "uninstall") == 0) {
        *out = DOM_SETUP_ACTION_UNINSTALL;
        return 1;
    }
    if (strcmp(value, "verify") == 0) {
        *out = DOM_SETUP_ACTION_VERIFY;
        return 1;
    }
    return 0;
}

static const char* dom_setup_cli_status_str(dom_setup_status st)
{
    switch (st) {
    case DOM_SETUP_STATUS_OK: return "ok";
    case DOM_SETUP_STATUS_ERROR: return "error";
    case DOM_SETUP_STATUS_INVALID_ARGUMENT: return "invalid_argument";
    case DOM_SETUP_STATUS_IO_ERROR: return "io_error";
    case DOM_SETUP_STATUS_PERMISSION_DENIED: return "permission_denied";
    default: break;
    }
    return "unknown";
}

static void dom_setup_cli_progress(const dom_setup_progress* prog, void* user)
{
    int quiet;
    const char* step;

    quiet = user ? *((int*)user) : 0;
    if (quiet || !prog) {
        return;
    }

    step = prog->current_step ? prog->current_step : "progress";
    printf("%s: %u/%u files, %lu/%lu bytes\n",
           step,
           (unsigned int)prog->files_done,
           (unsigned int)prog->files_total,
           (unsigned long)prog->bytes_done,
           (unsigned long)prog->bytes_total);
    fflush(stdout);
}

int main(int argc, char** argv)
{
    dom_setup_desc desc;
    dom_setup_command cmd;
    dom_core_desc core_desc;
    dom_core* core;
    void* setup_ctx;
    dom_setup_status status;
    int i;
    int show_usage;

    memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = 1u;
    desc.product_id = "dominium";
    desc.product_version = DOMINIUM_VERSION_SEMVER;
    desc.build_id = NULL;
    desc.scope = DOM_SETUP_SCOPE_PER_USER;
    desc.target_dir = NULL;
    desc.quiet = 0;
    desc.no_launcher = 0;
    desc.no_desktop_shortcuts = 0;

    memset(&cmd, 0, sizeof(cmd));
    cmd.struct_size = sizeof(cmd);
    cmd.struct_version = 1u;
    cmd.action = DOM_SETUP_ACTION_INSTALL;
    cmd.existing_install_dir = NULL;

    show_usage = 0;
    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (strncmp(arg, "--scope=", 8) == 0) {
            if (!dom_setup_cli_parse_scope(arg + 8, &desc.scope)) {
                show_usage = 1;
            }
        } else if (strncmp(arg, "--action=", 9) == 0) {
            if (!dom_setup_cli_parse_action(arg + 9, &cmd.action)) {
                show_usage = 1;
            }
        } else if (strncmp(arg, "--dir=", 6) == 0) {
            desc.target_dir = arg + 6;
            cmd.existing_install_dir = arg + 6;
        } else if (strcmp(arg, "--quiet") == 0) {
            desc.quiet = 1;
        } else {
            show_usage = 1;
        }
    }

    if (show_usage) {
        dom_setup_cli_print_usage();
        return 1;
    }

    core_desc.api_version = 1u;
    if (dsys_init() != DSYS_OK) {
        printf("Failed to initialize dsys\n");
        return 1;
    }

    core = dom_core_create(&core_desc);
    if (!core) {
        printf("Failed to create core\n");
        dsys_shutdown();
        return 1;
    }

    status = dom_setup_create(core, &desc, &setup_ctx);
    if (status != DOM_SETUP_STATUS_OK) {
        printf("dom_setup_create failed: %s\n", dom_setup_cli_status_str(status));
        dom_core_destroy(core);
        dsys_shutdown();
        return 1;
    }

    if (!cmd.existing_install_dir && desc.target_dir) {
        cmd.existing_install_dir = desc.target_dir;
    }

    status = dom_setup_execute(setup_ctx, &cmd,
                               desc.quiet ? NULL : dom_setup_cli_progress,
                               &desc.quiet);

    dom_setup_destroy(setup_ctx);
    dom_core_destroy(core);
    dsys_shutdown();

    if (status != DOM_SETUP_STATUS_OK) {
        printf("dom_setup_execute failed: %s\n", dom_setup_cli_status_str(status));
        return 1;
    }

    if (!desc.quiet) {
        printf("Action '%d' completed successfully.\n", (int)cmd.action);
    }
    return 0;
}
