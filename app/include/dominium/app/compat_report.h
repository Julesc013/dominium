/*
Shared compatibility report helper for app-layer consumers.
*/
#ifndef DOMINIUM_APP_COMPAT_REPORT_H
#define DOMINIUM_APP_COMPAT_REPORT_H

#include <stdint.h>
#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_app_compat_expect {
    int has_engine_version;
    int has_game_version;
    int has_build_id;
    int has_sim_schema_id;
    int has_build_info_abi;
    int has_caps_abi;
    int has_gfx_api;

    const char* engine_version;
    const char* game_version;
    const char* build_id;
    uint64_t    sim_schema_id;
    uint32_t    build_info_abi;
    uint32_t    caps_abi;
    uint32_t    gfx_api;
} dom_app_compat_expect;

typedef struct dom_app_compat_report {
    int          ok;
    const char*  product;
    const char*  engine_version;
    const char*  game_version;
    const char*  build_id;
    const char*  git_hash;
    const char*  toolchain_id;
    uint64_t     sim_schema_id;
    uint32_t     build_info_abi;
    uint32_t     build_info_struct_size;
    uint32_t     caps_abi;
    uint32_t     gfx_api;
    char         message[256];
} dom_app_compat_report;

void dom_app_compat_expect_init(dom_app_compat_expect* expect);
void dom_app_compat_report_init(dom_app_compat_report* report, const char* product);
int  dom_app_compat_check(const dom_app_compat_expect* expect,
                          dom_app_compat_report* report);
void dom_app_compat_print_report(const dom_app_compat_report* report,
                                 FILE* out_file);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_COMPAT_REPORT_H */
