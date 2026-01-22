/*
Stub launcher CLI entrypoint.
*/
#include "domino/control.h"
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/render/backend_detect.h"
#include "domino/sys.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "launcher/launcher.h"
#include "launcher/launcher_profile.h"

static void print_version(const char* product_version)
{
    printf("launcher %s\n", product_version);
}

static void print_build_info(const char* product_name, const char* product_version)
{
    printf("product=%s\n", product_name);
    printf("product_version=%s\n", product_version);
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("build_id=%s\n", DOM_BUILD_ID);
    printf("git_hash=%s\n", DOM_GIT_HASH);
    printf("toolchain_id=%s\n", DOM_TOOLCHAIN_ID);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\n");
    printf("abi_dom_build_info=%u\n", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    printf("abi_dom_caps=%u\n", (unsigned int)DOM_CAPS_ABI_VERSION);
    printf("api_dsys=%u\n", 1u);
    printf("api_dgfx=%u\n", (unsigned int)DGFX_PROTOCOL_VERSION);
}

static void print_control_caps(const dom_control_caps* caps)
{
    const dom_registry* reg = dom_control_caps_registry(caps);
    u32 i;
    u32 enabled = dom_control_caps_enabled_count(caps);
#if DOM_CONTROL_HOOKS
    printf("control_hooks=enabled\n");
#else
    printf("control_hooks=removed\n");
#endif
    printf("control_caps_enabled=%u\n", (unsigned int)enabled);
    if (!reg) {
        return;
    }
    for (i = 0u; i < reg->count; ++i) {
        const dom_registry_entry* entry = &reg->entries[i];
        if (dom_control_caps_is_enabled(caps, entry->id)) {
            printf("control_cap=%s\n", entry->key);
        }
    }
}

static int enable_control_list(dom_control_caps* caps, const char* list)
{
    char buf[512];
    size_t len;
    char* token;
    if (!list || !caps) {
        return 0;
    }
    len = strlen(list);
    if (len >= sizeof(buf)) {
        return -1;
    }
    memcpy(buf, list, len + 1u);
    token = buf;
    while (token) {
        char* comma = strchr(token, ',');
        if (comma) {
            *comma = '\0';
        }
        if (*token) {
            if (dom_control_caps_enable_key(caps, token) != DOM_CONTROL_OK) {
                return -1;
            }
        }
        token = comma ? (comma + 1u) : (char*)0;
    }
    return 0;
}

static void launcher_print_help(void)
{
    printf("usage: launcher [--help] [--version] [--build-info] [--status] [--smoke] [--selftest] <command>\n");
    printf("options:\n");
    printf("  --build-info                 Show build info + control capabilities\n");
    printf("  --status                     Show active control layers\n");
    printf("  --smoke                      Run deterministic CLI smoke\n");
    printf("  --selftest                   Alias for --smoke\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\n");
    printf("  --control-registry <path>    Override control registry path\n");
    printf("commands:\n");
    printf("  version         Show launcher version\n");
    printf("  list-profiles   List known profiles\n");
    printf("  capabilities    Report platform + renderer availability\n");
}

static void launcher_print_profiles(void)
{
    int count;
    int i;

    launcher_profile_load_all();
    count = launcher_profile_count();
    if (count <= 0) {
        printf("profiles: none\n");
        return;
    }

    for (i = 0; i < count; ++i) {
        const launcher_profile* p = launcher_profile_get(i);
        if (!p) {
            continue;
        }
        printf("%s\t%s\n", p->id, p->name);
    }
}

static const char* launcher_backend_name_for(d_gfx_backend_type backend,
                                             const d_gfx_backend_info* infos,
                                             u32 count)
{
    u32 i;
    for (i = 0u; i < count; ++i) {
        if (infos[i].backend == backend) {
            return infos[i].name;
        }
    }
    return "unknown";
}

static int launcher_print_capabilities(void)
{
    dsys_caps caps;
    d_gfx_backend_info infos[D_GFX_BACKEND_MAX];
    u32 count;
    d_gfx_backend_type auto_backend;
    const char* auto_name;
    int dsys_ok = 0;
    u32 i;

    if (dsys_init() == DSYS_OK) {
        caps = dsys_get_caps();
        dsys_ok = 1;
    } else {
        caps.name = "unknown";
        caps.ui_modes = 0u;
        caps.has_windows = false;
        caps.has_mouse = false;
        caps.has_gamepad = false;
        caps.has_high_res_timer = false;
        fprintf(stderr, "launcher: dsys_init failed (%s)\n", dsys_last_error_text());
    }

    printf("platform_backend=%s\n", caps.name ? caps.name : "unknown");
    printf("platform_ui_modes=%u\n", (unsigned int)caps.ui_modes);
    printf("platform_windows=%u\n", caps.has_windows ? 1u : 0u);
    printf("platform_mouse=%u\n", caps.has_mouse ? 1u : 0u);
    printf("platform_gamepad=%u\n", caps.has_gamepad ? 1u : 0u);
    printf("platform_hr_timer=%u\n", caps.has_high_res_timer ? 1u : 0u);

    count = d_gfx_detect_backends(infos, (u32)(sizeof(infos) / sizeof(infos[0])));
    auto_backend = d_gfx_select_backend();
    auto_name = launcher_backend_name_for(auto_backend, infos, count);
    printf("renderer_auto=%s\n", auto_name ? auto_name : "unknown");
    for (i = 0u; i < count; ++i) {
        printf("renderer=%s supported=%u detail=%s\n",
               infos[i].name,
               infos[i].supported ? 1u : 0u,
               infos[i].detail);
    }

    if (dsys_ok) {
        dsys_shutdown();
    }
    return dsys_ok ? 0 : 2;
}

int main(int argc, char** argv)
{
    const char* control_registry_path = "data/registries/control_capabilities.registry";
    const char* control_enable = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    const char* cmd = 0;
    int i;

    if (argc <= 1) {
        launcher_print_help();
        return 0;
    }

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            cmd = argv[i];
            break;
        }
        if (strcmp(argv[i], "--version") == 0) {
            cmd = argv[i];
            break;
        }
        if (strcmp(argv[i], "--build-info") == 0) {
            want_build_info = 1;
            continue;
        }
        if (strcmp(argv[i], "--status") == 0) {
            want_status = 1;
            continue;
        }
        if (strcmp(argv[i], "--smoke") == 0) {
            want_smoke = 1;
            continue;
        }
        if (strcmp(argv[i], "--selftest") == 0) {
            want_selftest = 1;
            continue;
        }
        if (strcmp(argv[i], "--control-registry") == 0 && i + 1 < argc) {
            control_registry_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--control-enable=", 17) == 0) {
            control_enable = argv[i] + 17;
            continue;
        }
        if (strcmp(argv[i], "--control-enable") == 0 && i + 1 < argc) {
            control_enable = argv[i + 1];
            i += 1;
            continue;
        }
        if (argv[i][0] != '-') {
            cmd = argv[i];
            break;
        }
    }
    if (want_smoke || want_selftest) {
        want_status = 1;
    }
    if (!cmd && !want_build_info && !want_status) {
        launcher_print_help();
        return 2;
    }

    if (strcmp(cmd, "--help") == 0 || strcmp(cmd, "-h") == 0) {
        launcher_print_help();
        return 0;
    }
    if (want_build_info || want_status) {
        dom_control_caps caps;
        if (dom_control_caps_init(&caps, control_registry_path) != DOM_CONTROL_OK) {
            fprintf(stderr, "launcher: failed to load control registry: %s\n", control_registry_path);
            return 2;
        }
        if (enable_control_list(&caps, control_enable) != 0) {
            fprintf(stderr, "launcher: invalid control capability list\n");
            dom_control_caps_free(&caps);
            return 2;
        }
        if (want_build_info) {
            print_build_info("launcher", DOMINIUM_LAUNCHER_VERSION);
        }
        print_control_caps(&caps);
        dom_control_caps_free(&caps);
        return 0;
    }
    if (!cmd) {
        launcher_print_help();
        return 2;
    }
    if (strcmp(cmd, "--version") == 0 || strcmp(cmd, "version") == 0) {
        print_version(DOMINIUM_LAUNCHER_VERSION);
        return 0;
    }
    if (strcmp(cmd, "list-profiles") == 0) {
        launcher_print_profiles();
        return 0;
    }
    if (strcmp(cmd, "capabilities") == 0) {
        return launcher_print_capabilities();
    }

    printf("launcher: unknown command '%s'\n", cmd);
    launcher_print_help();
    return 2;
}
