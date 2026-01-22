/*
Compatibility checks for app-layer entrypoints.
*/
#include "dominium/app/compat_report.h"

#include <string.h>

#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/gfx.h"
#include "domino/version.h"
#include "dom_contracts/version.h"

static void dom_app_compat_set_message(dom_app_compat_report* report, const char* msg)
{
    if (!report) {
        return;
    }
    if (!msg) {
        report->message[0] = '\0';
        return;
    }
    strncpy(report->message, msg, sizeof(report->message) - 1u);
    report->message[sizeof(report->message) - 1u] = '\0';
}

void dom_app_compat_expect_init(dom_app_compat_expect* expect)
{
    if (!expect) {
        return;
    }
    memset(expect, 0, sizeof(*expect));
}

void dom_app_compat_report_init(dom_app_compat_report* report, const char* product)
{
    if (!report) {
        return;
    }
    memset(report, 0, sizeof(*report));
    report->product = product;
}

int dom_app_compat_check(const dom_app_compat_expect* expect,
                         dom_app_compat_report* report)
{
    const dom_build_info_v1* build;
    const char* engine_version;
    const char* game_version;
    const char* build_id;
    const char* git_hash;
    const char* toolchain_id;

    if (!report) {
        return 0;
    }

    build = dom_build_info_v1_get();
    if (!build) {
        report->ok = 0;
        dom_app_compat_set_message(report, "build_info missing");
        return 0;
    }

    engine_version = DOMINO_VERSION_STRING;
    game_version = DOMINIUM_GAME_VERSION;
    build_id = dom_build_id();
    git_hash = dom_git_hash();
    toolchain_id = dom_toolchain_id();

    report->engine_version = engine_version;
    report->game_version = game_version;
    report->build_id = build_id;
    report->git_hash = git_hash;
    report->toolchain_id = toolchain_id;
    report->sim_schema_id = dom_sim_schema_id();
    report->build_info_abi = build->abi_version;
    report->build_info_struct_size = build->struct_size;
    report->caps_abi = DOM_CAPS_ABI_VERSION;
    report->gfx_api = DGFX_PROTOCOL_VERSION;

    if (build->abi_version != DOM_BUILD_INFO_ABI_VERSION ||
        build->struct_size != (uint32_t)sizeof(dom_build_info_v1)) {
        char buf[128];
        snprintf(buf, sizeof(buf),
                 "build_info abi mismatch (expected %u/%u found %u/%u)",
                 (unsigned int)DOM_BUILD_INFO_ABI_VERSION,
                 (unsigned int)sizeof(dom_build_info_v1),
                 (unsigned int)build->abi_version,
                 (unsigned int)build->struct_size);
        report->ok = 0;
        dom_app_compat_set_message(report, buf);
        return 0;
    }

    if (expect && expect->has_engine_version && expect->engine_version) {
        if (strcmp(expect->engine_version, engine_version) != 0) {
            char buf[128];
            snprintf(buf, sizeof(buf),
                     "engine_version mismatch (expected %s found %s)",
                     expect->engine_version, engine_version ? engine_version : "unknown");
            report->ok = 0;
            dom_app_compat_set_message(report, buf);
            return 0;
        }
    }
    if (expect && expect->has_game_version && expect->game_version) {
        if (strcmp(expect->game_version, game_version) != 0) {
            char buf[128];
            snprintf(buf, sizeof(buf),
                     "game_version mismatch (expected %s found %s)",
                     expect->game_version, game_version ? game_version : "unknown");
            report->ok = 0;
            dom_app_compat_set_message(report, buf);
            return 0;
        }
    }
    if (expect && expect->has_build_id && expect->build_id) {
        if (!build_id || strcmp(expect->build_id, build_id) != 0) {
            char buf[128];
            snprintf(buf, sizeof(buf),
                     "build_id mismatch (expected %s found %s)",
                     expect->build_id, build_id ? build_id : "unknown");
            report->ok = 0;
            dom_app_compat_set_message(report, buf);
            return 0;
        }
    }
    if (expect && expect->has_sim_schema_id) {
        if (expect->sim_schema_id != report->sim_schema_id) {
            char buf[128];
            snprintf(buf, sizeof(buf),
                     "sim_schema_id mismatch (expected %llu found %llu)",
                     (unsigned long long)expect->sim_schema_id,
                     (unsigned long long)report->sim_schema_id);
            report->ok = 0;
            dom_app_compat_set_message(report, buf);
            return 0;
        }
    }
    if (expect && expect->has_build_info_abi) {
        if (expect->build_info_abi != report->build_info_abi) {
            char buf[128];
            snprintf(buf, sizeof(buf),
                     "build_info_abi mismatch (expected %u found %u)",
                     (unsigned int)expect->build_info_abi,
                     (unsigned int)report->build_info_abi);
            report->ok = 0;
            dom_app_compat_set_message(report, buf);
            return 0;
        }
    }
    if (expect && expect->has_caps_abi) {
        if (expect->caps_abi != report->caps_abi) {
            char buf[128];
            snprintf(buf, sizeof(buf),
                     "caps_abi mismatch (expected %u found %u)",
                     (unsigned int)expect->caps_abi,
                     (unsigned int)report->caps_abi);
            report->ok = 0;
            dom_app_compat_set_message(report, buf);
            return 0;
        }
    }
    if (expect && expect->has_gfx_api) {
        if (expect->gfx_api != report->gfx_api) {
            char buf[128];
            snprintf(buf, sizeof(buf),
                     "gfx_api mismatch (expected %u found %u)",
                     (unsigned int)expect->gfx_api,
                     (unsigned int)report->gfx_api);
            report->ok = 0;
            dom_app_compat_set_message(report, buf);
            return 0;
        }
    }

    report->ok = 1;
    dom_app_compat_set_message(report, "ok");
    return 1;
}

void dom_app_compat_print_report(const dom_app_compat_report* report,
                                 FILE* out_file)
{
    FILE* out = out_file ? out_file : stdout;
    if (!report) {
        return;
    }
    fprintf(out, "compat_status=%s\n", report->ok ? "ok" : "failed");
    if (!report->ok && report->message[0]) {
        fprintf(out, "compat_error=%s\n", report->message);
    }
    fprintf(out, "engine_version=%s\n", report->engine_version ? report->engine_version : "");
    fprintf(out, "game_version=%s\n", report->game_version ? report->game_version : "");
    fprintf(out, "build_id=%s\n", report->build_id ? report->build_id : "");
    fprintf(out, "git_hash=%s\n", report->git_hash ? report->git_hash : "");
    fprintf(out, "toolchain_id=%s\n", report->toolchain_id ? report->toolchain_id : "");
    fprintf(out, "sim_schema_id=%llu\n", (unsigned long long)report->sim_schema_id);
    fprintf(out, "build_info_abi=%u\n", (unsigned int)report->build_info_abi);
    fprintf(out, "build_info_struct_size=%u\n", (unsigned int)report->build_info_struct_size);
    fprintf(out, "caps_abi=%u\n", (unsigned int)report->caps_abi);
    fprintf(out, "gfx_api=%u\n", (unsigned int)report->gfx_api);
}
