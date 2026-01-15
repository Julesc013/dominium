/*
FILE: source/dominium/common/dom_migration.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/migration
RESPONSIBILITY: Migration registration, path selection, and audit hooks.
*/
#include "dom_migration.h"

#include <algorithm>

namespace {

static bool migration_edge_less(const dom_migration_edge &a,
                                const dom_migration_edge &b) {
    if (a.schema_id != b.schema_id) {
        return a.schema_id < b.schema_id;
    }
    if (a.from_version != b.from_version) {
        return a.from_version < b.from_version;
    }
    return a.to_version < b.to_version;
}

static const dom_migration_edge *find_edge(const dom_schema_registry *registry,
                                           u64 schema_id,
                                           u32 from_version,
                                           u32 to_version) {
    size_t i;
    if (!registry) {
        return (const dom_migration_edge *)0;
    }
    for (i = 0u; i < registry->migrations.size(); ++i) {
        const dom_migration_edge &edge = registry->migrations[i];
        if (edge.schema_id == schema_id &&
            edge.from_version == from_version &&
            edge.to_version == to_version) {
            return &edge;
        }
    }
    return (const dom_migration_edge *)0;
}

} /* namespace */

int dom_migration_register(dom_schema_registry *registry,
                           const dom_migration_desc *desc) {
    size_t i;
    if (!registry || !desc || desc->schema_id == 0u ||
        desc->from_version == 0u || desc->to_version == 0u ||
        desc->from_version == desc->to_version) {
        return DOM_SCHEMA_REGISTRY_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->migrations.size(); ++i) {
        const dom_migration_edge &edge = registry->migrations[i];
        if (edge.schema_id == desc->schema_id &&
            edge.from_version == desc->from_version &&
            edge.to_version == desc->to_version) {
            return DOM_SCHEMA_REGISTRY_DUPLICATE;
        }
    }
    {
        dom_migration_edge edge;
        edge.schema_id = desc->schema_id;
        edge.from_version = desc->from_version;
        edge.to_version = desc->to_version;
        edge.fn = desc->fn;
        edge.user = desc->user;
        registry->migrations.push_back(edge);
        std::sort(registry->migrations.begin(),
                  registry->migrations.end(),
                  migration_edge_less);
    }
    return DOM_SCHEMA_REGISTRY_OK;
}

int dom_migration_find_path(const dom_schema_registry *registry,
                            u64 schema_id,
                            u32 from_version,
                            u32 to_version,
                            u32 *out_versions,
                            u32 out_cap,
                            u32 *out_count) {
    std::vector<u32> versions;
    std::vector<int> prev;
    std::vector<u32> queue;
    size_t q_index = 0u;
    int found_index = -1;

    if (!registry || !out_versions || !out_count ||
        schema_id == 0u || from_version == 0u || to_version == 0u) {
        return DOM_SCHEMA_REGISTRY_INVALID_ARGUMENT;
    }
    if (!dom_schema_registry_find(registry, schema_id)) {
        return DOM_SCHEMA_REGISTRY_NOT_FOUND;
    }
    if (from_version == to_version) {
        if (out_cap < 1u) {
            return DOM_SCHEMA_REGISTRY_ERR;
        }
        out_versions[0] = from_version;
        *out_count = 1u;
        return DOM_SCHEMA_REGISTRY_OK;
    }

    versions.push_back(from_version);
    prev.push_back(-1);
    queue.push_back(0u);

    while (q_index < queue.size()) {
        u32 cur_ver = versions[queue[q_index]];
        size_t i;
        ++q_index;

        if (cur_ver == to_version) {
            found_index = (int)queue[q_index - 1u];
            break;
        }

        for (i = 0u; i < registry->migrations.size(); ++i) {
            const dom_migration_edge &edge = registry->migrations[i];
            if (edge.schema_id != schema_id || edge.from_version != cur_ver) {
                continue;
            }
            {
                u32 next_ver = edge.to_version;
                bool seen = false;
                size_t v;
                for (v = 0u; v < versions.size(); ++v) {
                    if (versions[v] == next_ver) {
                        seen = true;
                        break;
                    }
                }
                if (seen) {
                    continue;
                }
                versions.push_back(next_ver);
                prev.push_back((int)queue[q_index - 1u]);
                queue.push_back((u32)(versions.size() - 1u));
            }
        }
    }

    if (found_index < 0) {
        return DOM_SCHEMA_REGISTRY_NO_PATH;
    }

    {
        std::vector<u32> rev;
        int idx = found_index;
        while (idx >= 0) {
            rev.push_back(versions[(size_t)idx]);
            idx = prev[(size_t)idx];
        }
        if (out_cap < (u32)rev.size()) {
            return DOM_SCHEMA_REGISTRY_ERR;
        }
        *out_count = (u32)rev.size();
        for (u32 i = 0u; i < *out_count; ++i) {
            out_versions[i] = rev[rev.size() - 1u - i];
        }
    }
    return DOM_SCHEMA_REGISTRY_OK;
}

int dom_migration_apply_chain(const dom_schema_registry *registry,
                              u64 schema_id,
                              u32 from_version,
                              u32 to_version,
                              const dom_migration_audit_sink *audit) {
    std::vector<u32> path;
    u32 count = 0u;
    int rc;
    u32 i;

    if (!registry) {
        return DOM_SCHEMA_REGISTRY_INVALID_ARGUMENT;
    }
    if (!dom_schema_registry_find(registry, schema_id)) {
        return DOM_SCHEMA_REGISTRY_NOT_FOUND;
    }

    path.resize(registry->migrations.size() + 1u);
    rc = dom_migration_find_path(registry,
                                 schema_id,
                                 from_version,
                                 to_version,
                                 path.empty() ? 0 : &path[0],
                                 (u32)path.size(),
                                 &count);
    if (rc != DOM_SCHEMA_REGISTRY_OK) {
        return rc;
    }
    if (count < 2u) {
        return DOM_SCHEMA_REGISTRY_OK;
    }

    for (i = 0u; i + 1u < count; ++i) {
        const dom_migration_edge *edge = find_edge(registry,
                                                   schema_id,
                                                   path[i],
                                                   path[i + 1u]);
        int step_rc = DOM_SCHEMA_REGISTRY_MIGRATION_FAILED;
        if (!edge || !edge->fn) {
            step_rc = DOM_SCHEMA_REGISTRY_MIGRATION_FAILED;
        } else {
            step_rc = edge->fn(schema_id, path[i], path[i + 1u], edge->user);
        }
        if (audit && audit->write) {
            dom_migration_audit_record rec;
            rec.schema_id = schema_id;
            rec.from_version = path[i];
            rec.to_version = path[i + 1u];
            rec.result = step_rc;
            audit->write(&rec, audit->user);
        }
        if (step_rc != DOM_SCHEMA_REGISTRY_OK) {
            return DOM_SCHEMA_REGISTRY_MIGRATION_FAILED;
        }
    }

    return DOM_SCHEMA_REGISTRY_OK;
}
