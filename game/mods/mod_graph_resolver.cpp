/*
FILE: game/mods/mod_graph_resolver.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Implements deterministic mod graph resolution and hashing.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Stable ordering and refusal-first resolution.
*/
#include "dominium/mods/mod_graph_resolver.h"

#include <cstring>

static void mod_graph_set_refusal(mod_graph_refusal* out_refusal,
                                  mod_graph_refusal_code code,
                                  const char* mod_id,
                                  const char* detail_id) {
    if (!out_refusal) {
        return;
    }
    out_refusal->code = code;
    if (mod_id) {
        std::strncpy(out_refusal->mod_id, mod_id, sizeof(out_refusal->mod_id) - 1u);
        out_refusal->mod_id[sizeof(out_refusal->mod_id) - 1u] = '\0';
    } else {
        out_refusal->mod_id[0] = '\0';
    }
    if (detail_id) {
        std::strncpy(out_refusal->detail_id, detail_id, sizeof(out_refusal->detail_id) - 1u);
        out_refusal->detail_id[sizeof(out_refusal->detail_id) - 1u] = '\0';
    } else {
        out_refusal->detail_id[0] = '\0';
    }
}

static int mod_id_compare(const char* a, const char* b) {
    if (!a || !b) {
        return 0;
    }
    return std::strcmp(a, b);
}

static void mod_swap_manifest(mod_manifest* a, mod_manifest* b) {
    mod_manifest tmp;
    tmp = *a;
    *a = *b;
    *b = tmp;
}

static int mod_find_index(const mod_graph* graph, const char* mod_id) {
    u32 i;
    if (!graph || !mod_id) {
        return -1;
    }
    for (i = 0u; i < graph->mod_count; ++i) {
        if (std::strcmp(graph->mods[i].mod_id, mod_id) == 0) {
            return (int)i;
        }
    }
    return -1;
}

int mod_graph_build(mod_graph* out_graph,
                    const mod_manifest* mods,
                    u32 mod_count,
                    mod_graph_refusal* out_refusal) {
    u32 i;
    u32 j;
    if (!out_graph || !mods) {
        mod_graph_set_refusal(out_refusal, MOD_GRAPH_ERR_TOO_MANY, "", "");
        return 1;
    }
    if (mod_count > DOM_MOD_MAX_MODS) {
        mod_graph_set_refusal(out_refusal, MOD_GRAPH_ERR_TOO_MANY, "", "");
        return 1;
    }
    out_graph->mod_count = mod_count;
    for (i = 0u; i < mod_count; ++i) {
        out_graph->mods[i] = mods[i];
        out_graph->order[i] = i;
    }
    for (i = 0u; i < mod_count; ++i) {
        u32 best = i;
        for (j = i + 1u; j < mod_count; ++j) {
            if (mod_id_compare(out_graph->mods[j].mod_id,
                               out_graph->mods[best].mod_id) < 0) {
                best = j;
            }
        }
        if (best != i) {
            mod_swap_manifest(&out_graph->mods[i], &out_graph->mods[best]);
        }
    }
    for (i = 1u; i < mod_count; ++i) {
        if (mod_id_compare(out_graph->mods[i - 1u].mod_id,
                           out_graph->mods[i].mod_id) == 0) {
            mod_graph_set_refusal(out_refusal, MOD_GRAPH_ERR_DUPLICATE,
                                  out_graph->mods[i].mod_id, "");
            return 1;
        }
    }
    return 0;
}

int mod_graph_resolve(mod_graph* graph,
                      mod_graph_refusal* out_refusal) {
    u32 i;
    u32 j;
    u32 count = 0u;
    d_bool added[DOM_MOD_MAX_MODS];
    if (!graph) {
        mod_graph_set_refusal(out_refusal, MOD_GRAPH_ERR_TOO_MANY, "", "");
        return 1;
    }
    for (i = 0u; i < graph->mod_count; ++i) {
        added[i] = D_FALSE;
    }
    for (i = 0u; i < graph->mod_count; ++i) {
        const mod_manifest* manifest = &graph->mods[i];
        for (j = 0u; j < manifest->dependency_count; ++j) {
            const mod_dependency* dep = &manifest->dependencies[j];
            int dep_index = mod_find_index(graph, dep->mod_id);
            if (dep_index < 0) {
                mod_graph_set_refusal(out_refusal, MOD_GRAPH_ERR_MISSING_DEP,
                                      manifest->mod_id, dep->mod_id);
                return 1;
            }
            if (!mod_version_in_range(&graph->mods[dep_index].mod_version, &dep->range)) {
                mod_graph_set_refusal(out_refusal, MOD_GRAPH_ERR_DEP_VERSION,
                                      manifest->mod_id, dep->mod_id);
                return 1;
            }
        }
        for (j = 0u; j < manifest->conflict_count; ++j) {
            const mod_conflict* conf = &manifest->conflicts[j];
            int conf_index = mod_find_index(graph, conf->mod_id);
            if (conf_index < 0) {
                continue;
            }
            if (mod_version_in_range(&graph->mods[conf_index].mod_version, &conf->range)) {
                mod_graph_set_refusal(out_refusal, MOD_GRAPH_ERR_CONFLICT,
                                      manifest->mod_id, conf->mod_id);
                return 1;
            }
        }
    }

    while (count < graph->mod_count) {
        int selected = -1;
        for (i = 0u; i < graph->mod_count; ++i) {
            const mod_manifest* manifest;
            d_bool deps_ok;
            if (added[i]) {
                continue;
            }
            manifest = &graph->mods[i];
            deps_ok = D_TRUE;
            for (j = 0u; j < manifest->dependency_count; ++j) {
                const mod_dependency* dep = &manifest->dependencies[j];
                int dep_index = mod_find_index(graph, dep->mod_id);
                if (dep_index < 0 || !added[dep_index]) {
                    deps_ok = D_FALSE;
                    break;
                }
            }
            if (deps_ok) {
                selected = (int)i;
                break;
            }
        }
        if (selected < 0) {
            mod_graph_set_refusal(out_refusal, MOD_GRAPH_ERR_CYCLE, "", "");
            return 1;
        }
        graph->order[count++] = (u32)selected;
        added[selected] = D_TRUE;
    }
    return 0;
}

static void mod_hash_sort_schema(mod_schema_version* schemas, u32 count) {
    u32 i;
    u32 j;
    for (i = 0u; i < count; ++i) {
        u32 best = i;
        for (j = i + 1u; j < count; ++j) {
            if (mod_id_compare(schemas[j].schema_id, schemas[best].schema_id) < 0) {
                best = j;
            }
        }
        if (best != i) {
            mod_schema_version tmp = schemas[i];
            schemas[i] = schemas[best];
            schemas[best] = tmp;
        }
    }
}

static void mod_hash_sort_epoch(mod_feature_epoch* epochs, u32 count) {
    u32 i;
    u32 j;
    for (i = 0u; i < count; ++i) {
        u32 best = i;
        for (j = i + 1u; j < count; ++j) {
            if (mod_id_compare(epochs[j].epoch_id, epochs[best].epoch_id) < 0) {
                best = j;
            }
        }
        if (best != i) {
            mod_feature_epoch tmp = epochs[i];
            epochs[i] = epochs[best];
            epochs[best] = tmp;
        }
    }
}

u64 mod_graph_identity_hash(const mod_graph* graph,
                            const mod_graph_identity_input* input) {
    u64 hash = mod_hash_fnv1a64_init();
    u32 i;
    if (!graph) {
        return 0u;
    }
    for (i = 0u; i < graph->mod_count; ++i) {
        const mod_manifest* manifest = &graph->mods[graph->order[i]];
        hash = mod_hash_fnv1a64_update_str(hash, manifest->mod_id);
        hash = mod_hash_fnv1a64_update(hash, &manifest->mod_version, sizeof(manifest->mod_version));
        hash = mod_hash_fnv1a64_update(hash, &manifest->payload_hash_value, sizeof(manifest->payload_hash_value));
        hash = mod_hash_fnv1a64_update(hash, &manifest->sim_affecting, sizeof(manifest->sim_affecting));
    }
    if (input && input->schemas && input->schema_count > 0u) {
        mod_schema_version sorted[DOM_MOD_MAX_SCHEMA_DEPS];
        u32 count = input->schema_count;
        if (count > DOM_MOD_MAX_SCHEMA_DEPS) {
            count = DOM_MOD_MAX_SCHEMA_DEPS;
        }
        for (i = 0u; i < count; ++i) {
            sorted[i] = input->schemas[i];
        }
        mod_hash_sort_schema(sorted, count);
        for (i = 0u; i < count; ++i) {
            hash = mod_hash_fnv1a64_update_str(hash, sorted[i].schema_id);
            hash = mod_hash_fnv1a64_update(hash, &sorted[i].version, sizeof(sorted[i].version));
        }
    }
    if (input && input->epochs && input->epoch_count > 0u) {
        mod_feature_epoch sorted_epochs[DOM_MOD_MAX_FEATURE_EPOCHS];
        u32 count = input->epoch_count;
        if (count > DOM_MOD_MAX_FEATURE_EPOCHS) {
            count = DOM_MOD_MAX_FEATURE_EPOCHS;
        }
        for (i = 0u; i < count; ++i) {
            sorted_epochs[i] = input->epochs[i];
        }
        mod_hash_sort_epoch(sorted_epochs, count);
        for (i = 0u; i < count; ++i) {
            hash = mod_hash_fnv1a64_update_str(hash, sorted_epochs[i].epoch_id);
            hash = mod_hash_fnv1a64_update(hash, &sorted_epochs[i].epoch, sizeof(sorted_epochs[i].epoch));
        }
    }
    return hash;
}

const char* mod_graph_refusal_to_string(mod_graph_refusal_code code) {
    switch (code) {
    case MOD_GRAPH_OK:
        return "OK";
    case MOD_GRAPH_ERR_TOO_MANY:
        return "TOO_MANY_MODS";
    case MOD_GRAPH_ERR_DUPLICATE:
        return "DUPLICATE_MOD";
    case MOD_GRAPH_ERR_MISSING_DEP:
        return "MISSING_DEPENDENCY";
    case MOD_GRAPH_ERR_DEP_VERSION:
        return "DEPENDENCY_VERSION_MISMATCH";
    case MOD_GRAPH_ERR_CONFLICT:
        return "CONFLICT";
    case MOD_GRAPH_ERR_CYCLE:
        return "CYCLE";
    default:
        return "UNKNOWN";
    }
}
