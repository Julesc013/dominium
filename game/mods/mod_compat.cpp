/*
FILE: game/mods/mod_compat.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Implements compatibility negotiation for mods.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic checks and refusal ordering.
*/
#include "dominium/mods/mod_compat.h"

#include <cstring>

static int mod_has_capability(const mod_required_capability* caps,
                              u32 cap_count,
                              const char* id) {
    u32 i;
    if (!id) {
        return 0;
    }
    for (i = 0u; i < cap_count; ++i) {
        if (std::strcmp(caps[i].capability_id, id) == 0) {
            return 1;
        }
    }
    return 0;
}

static int mod_has_render_feature(const mod_required_feature* feats,
                                  u32 feat_count,
                                  const char* id) {
    u32 i;
    if (!id) {
        return 0;
    }
    for (i = 0u; i < feat_count; ++i) {
        if (std::strcmp(feats[i].feature_id, id) == 0) {
            return 1;
        }
    }
    return 0;
}

static const mod_schema_version* mod_find_schema(const mod_compat_environment* env,
                                                 const char* schema_id) {
    u32 i;
    for (i = 0u; i < env->schema_count; ++i) {
        if (std::strcmp(env->schemas[i].schema_id, schema_id) == 0) {
            return &env->schemas[i];
        }
    }
    return 0;
}

static const mod_feature_epoch* mod_find_epoch(const mod_compat_environment* env,
                                               const char* epoch_id) {
    u32 i;
    for (i = 0u; i < env->epoch_count; ++i) {
        if (std::strcmp(env->epochs[i].epoch_id, epoch_id) == 0) {
            return &env->epochs[i];
        }
    }
    return 0;
}

int mod_compat_check_manifest(const mod_manifest* manifest,
                              const mod_compat_environment* env,
                              mod_compat_report* out_report) {
    u32 i;
    if (!manifest || !env || !out_report) {
        return 1;
    }
    out_report->result = MOD_COMPAT_ACCEPT;
    out_report->refusal = MOD_COMPAT_OK;
    out_report->warning_flags = 0u;

    for (i = 0u; i < manifest->schema_dep_count; ++i) {
        const mod_schema_dependency* dep = &manifest->schema_deps[i];
        const mod_schema_version* available = mod_find_schema(env, dep->schema_id);
        if (!available) {
            out_report->result = MOD_COMPAT_REFUSE;
            out_report->refusal = MOD_COMPAT_SCHEMA_MISSING;
            return 0;
        }
        if (!mod_version_in_range(&available->version, &dep->range)) {
            out_report->result = MOD_COMPAT_REFUSE;
            out_report->refusal = MOD_COMPAT_SCHEMA_RANGE;
            return 0;
        }
    }
    for (i = 0u; i < manifest->feature_epoch_count; ++i) {
        const mod_feature_epoch_req* req = &manifest->feature_epochs[i];
        const mod_feature_epoch* epoch = mod_find_epoch(env, req->epoch_id);
        if (!epoch) {
            out_report->result = MOD_COMPAT_REFUSE;
            out_report->refusal = MOD_COMPAT_EPOCH_MISSING;
            return 0;
        }
        if (req->has_min && epoch->epoch < req->min_epoch) {
            out_report->result = MOD_COMPAT_REFUSE;
            out_report->refusal = MOD_COMPAT_EPOCH_RANGE;
            return 0;
        }
        if (req->has_max && epoch->epoch > req->max_epoch) {
            out_report->result = MOD_COMPAT_REFUSE;
            out_report->refusal = MOD_COMPAT_EPOCH_RANGE;
            return 0;
        }
    }
    for (i = 0u; i < manifest->capability_count; ++i) {
        const mod_required_capability* cap = &manifest->capabilities[i];
        if (!mod_has_capability(env->capabilities, env->capability_count, cap->capability_id)) {
            out_report->result = MOD_COMPAT_REFUSE;
            out_report->refusal = MOD_COMPAT_CAPABILITY_MISSING;
            return 0;
        }
    }
    for (i = 0u; i < manifest->render_feature_count; ++i) {
        const mod_required_feature* feat = &manifest->render_features[i];
        if (!mod_has_render_feature(env->render_features, env->render_feature_count, feat->feature_id)) {
            out_report->result = MOD_COMPAT_REFUSE;
            out_report->refusal = MOD_COMPAT_RENDER_FEATURE_MISSING;
            return 0;
        }
    }
    if (manifest->perf_budget_class > env->perf_budget_class) {
        if (manifest->sim_affecting) {
            out_report->result = MOD_COMPAT_REFUSE;
            out_report->refusal = MOD_COMPAT_PERF_BUDGET;
            return 0;
        }
        out_report->result = MOD_COMPAT_ACCEPT_WITH_WARNINGS;
        out_report->warning_flags |= MOD_COMPAT_WARN_PERF_BUDGET;
    }
    return 0;
}

const char* mod_compat_result_to_string(mod_compat_result result) {
    switch (result) {
    case MOD_COMPAT_ACCEPT:
        return "ACCEPT";
    case MOD_COMPAT_ACCEPT_WITH_WARNINGS:
        return "ACCEPT_WITH_WARNINGS";
    case MOD_COMPAT_REFUSE:
        return "REFUSE";
    default:
        return "UNKNOWN";
    }
}

const char* mod_compat_refusal_to_string(mod_compat_refusal_code code) {
    switch (code) {
    case MOD_COMPAT_OK:
        return "OK";
    case MOD_COMPAT_SCHEMA_MISSING:
        return "SCHEMA_MISSING";
    case MOD_COMPAT_SCHEMA_RANGE:
        return "SCHEMA_RANGE";
    case MOD_COMPAT_EPOCH_MISSING:
        return "EPOCH_MISSING";
    case MOD_COMPAT_EPOCH_RANGE:
        return "EPOCH_RANGE";
    case MOD_COMPAT_CAPABILITY_MISSING:
        return "CAPABILITY_MISSING";
    case MOD_COMPAT_RENDER_FEATURE_MISSING:
        return "RENDER_FEATURE_MISSING";
    case MOD_COMPAT_PERF_BUDGET:
        return "PERF_BUDGET";
    default:
        return "UNKNOWN";
    }
}
