/*
FILE: source/dominium/game/runtime/dom_system_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/system_registry
RESPONSIBILITY: Deterministic system registry (IDs + ordering).
*/
#include "runtime/dom_system_registry.h"

#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct SystemEntry {
    dom_system_id id;
    dom_system_id parent_id;
    std::string string_id;
};

static int find_index(const std::vector<SystemEntry> &list, dom_system_id id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_sorted(std::vector<SystemEntry> &list, const SystemEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].id < entry.id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<SystemEntry>::difference_type)i, entry);
}

static int compute_hash_id(const char *bytes, u32 len, dom_system_id *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_SYSTEM_REGISTRY_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_SYSTEM_REGISTRY_INVALID_DATA;
    }
    if (hash == 0ull) {
        return DOM_SYSTEM_REGISTRY_INVALID_DATA;
    }
    *out_id = hash;
    return DOM_SYSTEM_REGISTRY_OK;
}

} // namespace

struct dom_system_registry {
    std::vector<SystemEntry> systems;
};

dom_system_registry *dom_system_registry_create(void) {
    return new dom_system_registry();
}

void dom_system_registry_destroy(dom_system_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_system_registry_register(dom_system_registry *registry,
                                 const dom_system_desc *desc) {
    dom_system_id id = 0ull;
    SystemEntry entry;
    if (!registry || !desc) {
        return DOM_SYSTEM_REGISTRY_INVALID_ARGUMENT;
    }
    if (desc->string_id && desc->string_id_len > 0u) {
        int rc = compute_hash_id(desc->string_id, desc->string_id_len, &id);
        if (rc != DOM_SYSTEM_REGISTRY_OK) {
            return rc;
        }
        if (desc->id != 0ull && desc->id != id) {
            return DOM_SYSTEM_REGISTRY_INVALID_DATA;
        }
    } else {
        id = desc->id;
    }
    if (id == 0ull) {
        return DOM_SYSTEM_REGISTRY_INVALID_DATA;
    }
    if (find_index(registry->systems, id) >= 0) {
        return DOM_SYSTEM_REGISTRY_DUPLICATE_ID;
    }
    entry.id = id;
    entry.parent_id = desc->parent_id;
    if (desc->string_id && desc->string_id_len > 0u) {
        entry.string_id.assign(desc->string_id, desc->string_id_len);
    } else {
        entry.string_id.clear();
    }
    insert_sorted(registry->systems, entry);
    return DOM_SYSTEM_REGISTRY_OK;
}

int dom_system_registry_get(const dom_system_registry *registry,
                            dom_system_id id,
                            dom_system_info *out_info) {
    int idx;
    if (!registry || !out_info) {
        return DOM_SYSTEM_REGISTRY_INVALID_ARGUMENT;
    }
    idx = find_index(registry->systems, id);
    if (idx < 0) {
        return DOM_SYSTEM_REGISTRY_NOT_FOUND;
    }
    {
        const SystemEntry &entry = registry->systems[(size_t)idx];
        out_info->id = entry.id;
        out_info->parent_id = entry.parent_id;
        out_info->string_id = entry.string_id.empty() ? 0 : entry.string_id.c_str();
        out_info->string_id_len = (u32)entry.string_id.size();
    }
    return DOM_SYSTEM_REGISTRY_OK;
}

int dom_system_registry_iterate(const dom_system_registry *registry,
                                dom_system_iter_fn fn,
                                void *user) {
    size_t i;
    if (!registry || !fn) {
        return DOM_SYSTEM_REGISTRY_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->systems.size(); ++i) {
        const SystemEntry &entry = registry->systems[i];
        dom_system_info info;
        info.id = entry.id;
        info.parent_id = entry.parent_id;
        info.string_id = entry.string_id.empty() ? 0 : entry.string_id.c_str();
        info.string_id_len = (u32)entry.string_id.size();
        fn(&info, user);
    }
    return DOM_SYSTEM_REGISTRY_OK;
}

u32 dom_system_registry_count(const dom_system_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->systems.size();
}

int dom_system_registry_add_baseline(dom_system_registry *registry) {
    dom_system_desc desc;
    dom_system_id galaxy_id = 0ull;
    int rc;

    if (!registry) {
        return DOM_SYSTEM_REGISTRY_INVALID_ARGUMENT;
    }
    rc = compute_hash_id("milky_way", 9u, &galaxy_id);
    if (rc != DOM_SYSTEM_REGISTRY_OK) {
        return rc;
    }
    desc.string_id = "sol";
    desc.string_id_len = 3u;
    desc.id = 0ull;
    desc.parent_id = galaxy_id;
    rc = dom_system_registry_register(registry, &desc);
    if (rc == DOM_SYSTEM_REGISTRY_DUPLICATE_ID) {
        return DOM_SYSTEM_REGISTRY_OK;
    }
    return rc;
}
