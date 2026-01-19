/*
FILE: game/include/dominium/mods/mod_safe_mode.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Deterministic safe-mode application for incompatible mods.
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and refusal.
*/
#ifndef DOMINIUM_MODS_MOD_SAFE_MODE_H
#define DOMINIUM_MODS_MOD_SAFE_MODE_H

#include "domino/core/types.h"
#include "dominium/mods/mod_compat.h"
#include "dominium/mods/mod_graph_resolver.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum mod_safe_mode_policy {
    MOD_SAFE_MODE_NONE = 0,
    MOD_SAFE_MODE_NON_SIM_ONLY = 1,
    MOD_SAFE_MODE_BASE_ONLY = 2
} mod_safe_mode_policy;

typedef enum mod_safe_mode_status {
    MOD_SAFE_STATUS_ENABLED = 0,
    MOD_SAFE_STATUS_DISABLED_SAFE_MODE = 1,
    MOD_SAFE_STATUS_DISABLED_INCOMPATIBLE = 2
} mod_safe_mode_status;

typedef enum mod_safe_mode_result_code {
    MOD_SAFE_MODE_OK = 0,
    MOD_SAFE_MODE_REFUSED = 1,
    MOD_SAFE_MODE_INVALID = 2
} mod_safe_mode_result_code;

typedef struct mod_safe_mode_entry {
    char mod_id[DOM_MOD_ID_MAX];
    mod_safe_mode_status status;
} mod_safe_mode_entry;

typedef struct mod_safe_mode_result {
    mod_safe_mode_result_code code;
    mod_safe_mode_entry entries[DOM_MOD_MAX_MODS];
    u32 entry_count;
} mod_safe_mode_result;

int mod_safe_mode_apply(const mod_graph* graph,
                        const mod_compat_report* reports,
                        u32 report_count,
                        mod_safe_mode_policy policy,
                        mod_safe_mode_result* out_result);
const char* mod_safe_mode_policy_to_string(mod_safe_mode_policy policy);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_MODS_MOD_SAFE_MODE_H */
