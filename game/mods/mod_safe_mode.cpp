/*
FILE: game/mods/mod_safe_mode.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Implements deterministic safe-mode filtering for mods.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and refusal.
*/
#include "dominium/mods/mod_safe_mode.h"

#include <cstring>

int mod_safe_mode_apply(const mod_graph* graph,
                        const mod_compat_report* reports,
                        u32 report_count,
                        mod_safe_mode_policy policy,
                        mod_safe_mode_result* out_result) {
    u32 i;
    if (!graph || !reports || !out_result || report_count != graph->mod_count) {
        if (out_result) {
            out_result->code = MOD_SAFE_MODE_INVALID;
            out_result->entry_count = 0u;
        }
        return 1;
    }
    out_result->entry_count = graph->mod_count;
    for (i = 0u; i < graph->mod_count; ++i) {
        const mod_manifest* manifest = &graph->mods[graph->order[i]];
        mod_safe_mode_entry* entry = &out_result->entries[i];
        std::strncpy(entry->mod_id, manifest->mod_id, sizeof(entry->mod_id) - 1u);
        entry->mod_id[sizeof(entry->mod_id) - 1u] = '\0';

        if (policy == MOD_SAFE_MODE_BASE_ONLY) {
            entry->status = MOD_SAFE_STATUS_DISABLED_SAFE_MODE;
            continue;
        }
        if (policy == MOD_SAFE_MODE_NON_SIM_ONLY && manifest->sim_affecting) {
            entry->status = MOD_SAFE_STATUS_DISABLED_SAFE_MODE;
            continue;
        }

        if (reports[i].result == MOD_COMPAT_REFUSE) {
            if (policy == MOD_SAFE_MODE_NONE) {
                out_result->code = MOD_SAFE_MODE_REFUSED;
                return 1;
            }
            entry->status = MOD_SAFE_STATUS_DISABLED_INCOMPATIBLE;
        } else {
            entry->status = MOD_SAFE_STATUS_ENABLED;
        }
    }
    out_result->code = MOD_SAFE_MODE_OK;
    return 0;
}

const char* mod_safe_mode_policy_to_string(mod_safe_mode_policy policy) {
    switch (policy) {
    case MOD_SAFE_MODE_NONE:
        return "NONE";
    case MOD_SAFE_MODE_NON_SIM_ONLY:
        return "NON_SIM_ONLY";
    case MOD_SAFE_MODE_BASE_ONLY:
        return "BASE_ONLY";
    default:
        return "UNKNOWN";
    }
}
