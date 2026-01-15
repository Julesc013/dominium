#include "dsk_resolve.h"

#include "dsk/dsk_digest.h"

#include <algorithm>

struct dsk_selected_source_t {
    std::string id;
    dsk_u16 source;
};

static const dsk_manifest_component_t *dsk_find_component(const dsk_manifest_t &manifest,
                                                          const std::string &id) {
    size_t i;
    for (i = 0u; i < manifest.components.size(); ++i) {
        if (manifest.components[i].component_id == id) {
            return &manifest.components[i];
        }
    }
    return 0;
}

static int dsk_is_selected(const std::vector<std::string> &selected,
                           const std::string &id) {
    return std::find(selected.begin(), selected.end(), id) != selected.end();
}

static int dsk_is_excluded(const std::vector<std::string> &excluded,
                           const std::string &id) {
    return std::find(excluded.begin(), excluded.end(), id) != excluded.end();
}

static dsk_u16 dsk_merge_source(dsk_u16 existing, dsk_u16 incoming) {
    if (incoming == DSK_PLAN_COMPONENT_SOURCE_USER) {
        return incoming;
    }
    if (existing == DSK_PLAN_COMPONENT_SOURCE_USER) {
        return existing;
    }
    if (incoming == DSK_PLAN_COMPONENT_SOURCE_DEPENDENCY) {
        return incoming;
    }
    if (existing == DSK_PLAN_COMPONENT_SOURCE_DEPENDENCY) {
        return existing;
    }
    if (incoming == DSK_PLAN_COMPONENT_SOURCE_DEFAULT) {
        return incoming;
    }
    return existing ? existing : incoming;
}

static void dsk_set_source(std::vector<dsk_selected_source_t> &sources,
                           const std::string &id,
                           dsk_u16 source) {
    size_t i;
    for (i = 0u; i < sources.size(); ++i) {
        if (sources[i].id == id) {
            sources[i].source = dsk_merge_source(sources[i].source, source);
            return;
        }
    }
    dsk_selected_source_t entry;
    entry.id = id;
    entry.source = source;
    sources.push_back(entry);
}

static dsk_u16 dsk_get_source(const std::vector<dsk_selected_source_t> &sources,
                              const std::string &id) {
    size_t i;
    for (i = 0u; i < sources.size(); ++i) {
        if (sources[i].id == id) {
            return sources[i].source;
        }
    }
    return DSK_PLAN_COMPONENT_SOURCE_DEFAULT;
}

static void dsk_add_refusal(std::vector<dsk_plan_refusal_t> *out_refusals,
                            dsk_u16 code,
                            const std::string &detail) {
    if (!out_refusals) {
        return;
    }
    dsk_plan_refusal_t refusal;
    refusal.code = code;
    refusal.detail = detail;
    out_refusals->push_back(refusal);
}

static dsk_status_t dsk_refusal_status(dsk_u16 refusal_code) {
    dsk_u16 subcode = DSK_SUBCODE_INVALID_FIELD;
    switch (refusal_code) {
    case DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND:
        subcode = DSK_SUBCODE_COMPONENT_NOT_FOUND;
        break;
    case DSK_PLAN_REFUSAL_UNSATISFIED_DEPENDENCY:
        subcode = DSK_SUBCODE_UNSATISFIED_DEPENDENCY;
        break;
    case DSK_PLAN_REFUSAL_EXPLICIT_CONFLICT:
        subcode = DSK_SUBCODE_EXPLICIT_CONFLICT;
        break;
    case DSK_PLAN_REFUSAL_PLATFORM_INCOMPATIBLE:
        subcode = DSK_SUBCODE_PLATFORM_INCOMPATIBLE;
        break;
    case DSK_PLAN_REFUSAL_ALREADY_INSTALLED:
        subcode = DSK_SUBCODE_ALREADY_INSTALLED;
        break;
    case DSK_PLAN_REFUSAL_NOT_INSTALLED:
        subcode = DSK_SUBCODE_NOT_INSTALLED;
        break;
    case DSK_PLAN_REFUSAL_STATE_MISMATCH:
        subcode = DSK_SUBCODE_STATE_MISMATCH;
        break;
    case DSK_PLAN_REFUSAL_MANIFEST_MISMATCH:
        subcode = DSK_SUBCODE_MANIFEST_MISMATCH;
        break;
    case DSK_PLAN_REFUSAL_DOWNGRADE_BLOCKED:
        subcode = DSK_SUBCODE_DOWNGRADE_BLOCKED;
        break;
    default:
        subcode = DSK_SUBCODE_INVALID_FIELD;
        break;
    }
    return dsk_error_make(DSK_DOMAIN_KERNEL,
                          DSK_CODE_VALIDATION_ERROR,
                          subcode,
                          DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static int dsk_component_supports_platform(const dsk_manifest_component_t *comp,
                                           const std::string &platform) {
    size_t i;
    if (!comp || comp->supported_targets.empty()) {
        return 1;
    }
    for (i = 0u; i < comp->supported_targets.size(); ++i) {
        if (comp->supported_targets[i] == platform) {
            return 1;
        }
    }
    return 0;
}

static int dsk_depends_on(const dsk_manifest_t &manifest,
                          const std::string &start,
                          const std::string &target) {
    std::vector<std::string> stack;
    std::vector<std::string> visited;
    size_t i;

    stack.push_back(start);
    while (!stack.empty()) {
        std::string cur = stack.back();
        stack.pop_back();
        if (std::find(visited.begin(), visited.end(), cur) != visited.end()) {
            continue;
        }
        visited.push_back(cur);
        const dsk_manifest_component_t *comp = dsk_find_component(manifest, cur);
        if (!comp) {
            continue;
        }
        for (i = 0u; i < comp->deps.size(); ++i) {
            if (comp->deps[i] == target) {
                return 1;
            }
            stack.push_back(comp->deps[i]);
        }
    }
    return 0;
}

static dsk_u64 dsk_resolved_digest(const std::vector<dsk_resolved_component_t> &components) {
    dsk_u64 hash = dsk_digest64_init();
    size_t i;
    const dsk_u8 zero = 0u;
    for (i = 0u; i < components.size(); ++i) {
        hash = dsk_digest64_update(hash,
                                   (const dsk_u8 *)components[i].component_id.c_str(),
                                   (dsk_u32)components[i].component_id.size());
        hash = dsk_digest64_update(hash, &zero, 1u);
        hash = dsk_digest64_update(hash,
                                   (const dsk_u8 *)components[i].component_version.c_str(),
                                   (dsk_u32)components[i].component_version.size());
        hash = dsk_digest64_update(hash, &zero, 1u);
    }
    return hash;
}

static bool dsk_string_less(const std::string &a, const std::string &b) {
    return a < b;
}

dsk_status_t dsk_resolve_components(const dsk_manifest_t &manifest,
                                    const dsk_request_t &request,
                                    const std::string &platform_triple,
                                    dsk_resolved_set_t *out_set,
                                    std::vector<dsk_plan_refusal_t> *out_refusals) {
    std::vector<std::string> selected;
    std::vector<std::string> excluded = request.excluded_components;
    std::vector<dsk_selected_source_t> sources;
    std::vector<std::string> incompatible;
    size_t i;

    if (!out_set) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    out_set->components.clear();
    out_set->digest64 = 0u;
    if (out_refusals) {
        out_refusals->clear();
    }

    if (!request.requested_components.empty()) {
        for (i = 0u; i < request.requested_components.size(); ++i) {
            const std::string &id = request.requested_components[i];
            if (!dsk_find_component(manifest, id)) {
                dsk_add_refusal(out_refusals, DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND, id);
                return dsk_refusal_status(DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND);
            }
            if (!dsk_is_selected(selected, id)) {
                selected.push_back(id);
            }
            dsk_set_source(sources, id, DSK_PLAN_COMPONENT_SOURCE_USER);
        }
    } else {
        for (i = 0u; i < manifest.components.size(); ++i) {
            if (manifest.components[i].default_selected) {
                selected.push_back(manifest.components[i].component_id);
                dsk_set_source(sources,
                               manifest.components[i].component_id,
                               DSK_PLAN_COMPONENT_SOURCE_DEFAULT);
            }
        }
    }

    for (i = 0u; i < excluded.size(); ++i) {
        if (!dsk_find_component(manifest, excluded[i])) {
            dsk_add_refusal(out_refusals, DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND, excluded[i]);
            return dsk_refusal_status(DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND);
        }
        if (dsk_is_selected(selected, excluded[i])) {
            selected.erase(std::remove(selected.begin(), selected.end(), excluded[i]), selected.end());
        }
    }

    {
        int changed = 1;
        while (changed) {
            changed = 0;
            for (i = 0u; i < selected.size(); ++i) {
                const dsk_manifest_component_t *comp = dsk_find_component(manifest, selected[i]);
                size_t j;
                if (!comp) {
                    dsk_add_refusal(out_refusals, DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND, selected[i]);
                    return dsk_refusal_status(DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND);
                }
                for (j = 0u; j < comp->deps.size(); ++j) {
                    const std::string &dep = comp->deps[j];
                    if (dsk_is_excluded(excluded, dep)) {
                        dsk_add_refusal(out_refusals,
                                        DSK_PLAN_REFUSAL_UNSATISFIED_DEPENDENCY,
                                        comp->component_id + "->" + dep);
                        return dsk_refusal_status(DSK_PLAN_REFUSAL_UNSATISFIED_DEPENDENCY);
                    }
                    if (!dsk_find_component(manifest, dep)) {
                        dsk_add_refusal(out_refusals,
                                        DSK_PLAN_REFUSAL_UNSATISFIED_DEPENDENCY,
                                        comp->component_id + "->" + dep);
                        return dsk_refusal_status(DSK_PLAN_REFUSAL_UNSATISFIED_DEPENDENCY);
                    }
                    if (!dsk_is_selected(selected, dep)) {
                        selected.push_back(dep);
                        dsk_set_source(sources, dep, DSK_PLAN_COMPONENT_SOURCE_DEPENDENCY);
                        changed = 1;
                    }
                }
            }
        }
    }

    for (i = 0u; i < selected.size(); ++i) {
        const dsk_manifest_component_t *comp = dsk_find_component(manifest, selected[i]);
        size_t j;
        if (!comp) {
            dsk_add_refusal(out_refusals, DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND, selected[i]);
            return dsk_refusal_status(DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND);
        }
        for (j = 0u; j < comp->conflicts.size(); ++j) {
            if (dsk_is_selected(selected, comp->conflicts[j])) {
                dsk_add_refusal(out_refusals,
                                DSK_PLAN_REFUSAL_EXPLICIT_CONFLICT,
                                comp->component_id + "<->" + comp->conflicts[j]);
                return dsk_refusal_status(DSK_PLAN_REFUSAL_EXPLICIT_CONFLICT);
            }
        }
    }

    for (i = 0u; i < selected.size(); ++i) {
        const dsk_manifest_component_t *comp = dsk_find_component(manifest, selected[i]);
        if (!dsk_component_supports_platform(comp, platform_triple)) {
            incompatible.push_back(selected[i]);
        }
    }

    for (i = 0u; i < incompatible.size(); ++i) {
        size_t j;
        const std::string &bad = incompatible[i];
        dsk_u16 src = dsk_get_source(sources, bad);
        if (src == DSK_PLAN_COMPONENT_SOURCE_USER) {
            dsk_add_refusal(out_refusals,
                            DSK_PLAN_REFUSAL_PLATFORM_INCOMPATIBLE,
                            bad);
            return dsk_refusal_status(DSK_PLAN_REFUSAL_PLATFORM_INCOMPATIBLE);
        }
        for (j = 0u; j < selected.size(); ++j) {
            if (selected[j] == bad) {
                continue;
            }
            if (dsk_depends_on(manifest, selected[j], bad)) {
                dsk_add_refusal(out_refusals,
                                DSK_PLAN_REFUSAL_PLATFORM_INCOMPATIBLE,
                                selected[j] + "->" + bad);
                return dsk_refusal_status(DSK_PLAN_REFUSAL_PLATFORM_INCOMPATIBLE);
            }
        }
    }

    for (i = 0u; i < incompatible.size(); ++i) {
        const std::string &bad = incompatible[i];
        selected.erase(std::remove(selected.begin(), selected.end(), bad), selected.end());
    }

    std::sort(selected.begin(), selected.end(), dsk_string_less);
    for (i = 0u; i < selected.size(); ++i) {
        const dsk_manifest_component_t *comp = dsk_find_component(manifest, selected[i]);
        dsk_resolved_component_t resolved;
        if (!comp) {
            dsk_add_refusal(out_refusals, DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND, selected[i]);
            return dsk_refusal_status(DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND);
        }
        resolved.component_id = comp->component_id;
        resolved.component_version = comp->component_version.empty()
            ? manifest.version
            : comp->component_version;
        resolved.kind = comp->kind;
        resolved.source = dsk_get_source(sources, comp->component_id);
        out_set->components.push_back(resolved);
    }

    out_set->digest64 = dsk_resolved_digest(out_set->components);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
