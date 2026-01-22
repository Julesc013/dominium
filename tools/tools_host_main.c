/*
Stub tools host entrypoint; replace with tool router once runtime is wired.
*/
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"

#include <stdio.h>
#include <string.h>

static void tools_print_help(void)
{
    printf("usage: tools [options] <command>\\n");
    printf("options:\\n");
    printf("  --help                      Show this help\\n");
    printf("  --version                   Show product version\\n");
    printf("  --build-info                Show build info\\n");
    printf("  --status                    Show tools status\\n");
    printf("  --smoke                     Run deterministic CLI smoke\\n");
    printf("  --selftest                  Alias for --smoke\\n");
    printf("commands:\\n");
    printf("  inspect    Inspect artifacts (stub)\\n");
    printf("  validate   Validate artifacts (stub)\\n");
    printf("  replay     Replay viewer (stub)\\n");
}

static void tools_print_version(const char* product_version)
{
    printf("tools %s\\n", product_version);
}

static void tools_print_build_info(const char* product_name, const char* product_version)
{
    printf("product=%s\\n", product_name);
    printf("product_version=%s\\n", product_version);
    printf("engine_version=%s\\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("build_id=%s\\n", DOM_BUILD_ID);
    printf("git_hash=%s\\n", DOM_GIT_HASH);
    printf("toolchain_id=%s\\n", DOM_TOOLCHAIN_ID);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\\n");
    printf("abi_dom_build_info=%u\\n", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    printf("abi_dom_caps=%u\\n", (unsigned int)DOM_CAPS_ABI_VERSION);
    printf("api_dsys=%u\\n", 1u);
    printf("api_dgfx=%u\\n", (unsigned int)DGFX_PROTOCOL_VERSION);
}

int main(int argc, char** argv)
{
    int want_help = 0;
    int want_version = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    const char* cmd = 0;
    int i;

    if (argc <= 1) {
        tools_print_help();
        return 0;
    }

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            want_help = 1;
            continue;
        }
        if (strcmp(argv[i], "--version") == 0) {
            want_version = 1;
            continue;
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
        if (argv[i][0] != '-') {
            cmd = argv[i];
            break;
        }
    }

    if (want_help) {
        tools_print_help();
        return 0;
    }
    if (want_version) {
        tools_print_version(DOMINIUM_TOOLS_VERSION);
        return 0;
    }
    if (want_smoke || want_selftest) {
        want_status = 1;
    }
    if (want_build_info) {
        tools_print_build_info("tools", DOMINIUM_TOOLS_VERSION);
    }
    if (want_status) {
        if (want_smoke || want_selftest) {
            printf("tools_smoke=ok\\n");
        } else {
            printf("tools_status=ok\\n");
        }
        if (!cmd) {
            return 0;
        }
    }
    if (!cmd) {
        tools_print_help();
        return 2;
    }

    if (strcmp(cmd, "inspect") == 0) {
        printf("tools: inspect stub\\n");
        return 0;
    }
    if (strcmp(cmd, "validate") == 0) {
        printf("tools: validate stub\\n");
        return 0;
    }
    if (strcmp(cmd, "replay") == 0) {
        printf("tools: replay stub\\n");
        return 0;
    }

    printf("tools: unknown command '%s'\\n", cmd);
    tools_print_help();
    return 2;
}
