/*
FILE: game/include/dominium/mods/mod_compat.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Compatibility negotiation for mods against schema and features.
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic checks and refusal ordering.
*/
#ifndef DOMINIUM_MODS_MOD_COMPAT_H
#define DOMINIUM_MODS_MOD_COMPAT_H

#include "domino/core/types.h"
#include "dominium/mods/mod_manifest.h"
#include "dominium/mods/mod_graph_resolver.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum mod_compat_result {
    MOD_COMPAT_ACCEPT = 0,
    MOD_COMPAT_ACCEPT_WITH_WARNINGS = 1,
    MOD_COMPAT_REFUSE = 2
} mod_compat_result;

typedef enum mod_compat_refusal_code {
    MOD_COMPAT_OK = 0,
    MOD_COMPAT_SCHEMA_MISSING = 1,
    MOD_COMPAT_SCHEMA_RANGE = 2,
    MOD_COMPAT_EPOCH_MISSING = 3,
    MOD_COMPAT_EPOCH_RANGE = 4,
    MOD_COMPAT_CAPABILITY_MISSING = 5,
    MOD_COMPAT_RENDER_FEATURE_MISSING = 6,
    MOD_COMPAT_PERF_BUDGET = 7
} mod_compat_refusal_code;

enum {
    MOD_COMPAT_WARN_PERF_BUDGET = 1u << 0
};

typedef struct mod_compat_environment {
    const mod_schema_version* schemas;
    u32 schema_count;
    const mod_feature_epoch* epochs;
    u32 epoch_count;
    const mod_required_capability* capabilities;
    u32 capability_count;
    const mod_required_feature* render_features;
    u32 render_feature_count;
    u32 perf_budget_class;
} mod_compat_environment;

typedef struct mod_compat_report {
    mod_compat_result result;
    mod_compat_refusal_code refusal;
    u32 warning_flags;
} mod_compat_report;

int mod_compat_check_manifest(const mod_manifest* manifest,
                              const mod_compat_environment* env,
                              mod_compat_report* out_report);
const char* mod_compat_result_to_string(mod_compat_result result);
const char* mod_compat_refusal_to_string(mod_compat_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_MODS_MOD_COMPAT_H */
