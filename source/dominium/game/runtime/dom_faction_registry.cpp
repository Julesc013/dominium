/*
FILE: source/dominium/game/runtime/dom_faction_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/faction_registry
RESPONSIBILITY: Deterministic faction registry + resource storage.
*/
#include "runtime/dom_faction_registry.h"

#include <algorithm>
#include <vector>
#include <climits>

namespace {

struct FactionEntry {
    dom_faction_id faction_id;
    u32 home_scope_kind;
    u64 home_scope_id;
    u32 policy_kind;
    u32 policy_flags;
    u64 ai_seed;
    std::vector<u64> known_nodes;
    std::vector<dom_faction_resource_entry> resources;
};

static int find_faction_index(const std::vector<FactionEntry> &list,
                              dom_faction_id faction_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].faction_id == faction_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_faction_sorted(std::vector<FactionEntry> &list,
                                  const FactionEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].faction_id < entry.faction_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<FactionEntry>::difference_type)i, entry);
}

static bool node_less(u64 a, u64 b) {
    return a < b;
}

static int find_resource_index(const std::vector<dom_faction_resource_entry> &list,
                               dom_resource_id resource_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].resource_id == resource_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_resource_sorted(std::vector<dom_faction_resource_entry> &list,
                                   const dom_faction_resource_entry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].resource_id < entry.resource_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<dom_faction_resource_entry>::difference_type)i,
                entry);
}

static bool delta_less(const dom_faction_resource_delta &a,
                       const dom_faction_resource_delta &b) {
    return a.resource_id < b.resource_id;
}

} // namespace

struct dom_faction_registry {
    std::vector<FactionEntry> factions;
};

dom_faction_registry *dom_faction_registry_create(void) {
    dom_faction_registry *registry = new dom_faction_registry();
    if (!registry) {
        return 0;
    }
    (void)dom_faction_registry_init(registry);
    return registry;
}

void dom_faction_registry_destroy(dom_faction_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_faction_registry_init(dom_faction_registry *registry) {
    if (!registry) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    registry->factions.clear();
    return DOM_FACTION_OK;
}

int dom_faction_register(dom_faction_registry *registry,
                         const dom_faction_desc *desc) {
    FactionEntry entry;
    if (!registry || !desc) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    if (desc->faction_id == 0ull || desc->home_scope_id == 0ull || desc->ai_seed == 0ull) {
        return DOM_FACTION_INVALID_DATA;
    }
    if (desc->home_scope_kind != DOM_MACRO_SCOPE_SYSTEM &&
        desc->home_scope_kind != DOM_MACRO_SCOPE_GALAXY) {
        return DOM_FACTION_INVALID_DATA;
    }
    if (desc->policy_kind > DOM_FACTION_POLICY_CONSERVE) {
        return DOM_FACTION_INVALID_DATA;
    }
    if (desc->known_node_count > 0u && !desc->known_nodes) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    if (find_faction_index(registry->factions, desc->faction_id) >= 0) {
        return DOM_FACTION_DUPLICATE_ID;
    }

    entry.faction_id = desc->faction_id;
    entry.home_scope_kind = desc->home_scope_kind;
    entry.home_scope_id = desc->home_scope_id;
    entry.policy_kind = desc->policy_kind;
    entry.policy_flags = desc->policy_flags;
    entry.ai_seed = desc->ai_seed;
    entry.resources.clear();
    entry.known_nodes.clear();
    if (desc->known_node_count > 0u) {
        entry.known_nodes.assign(desc->known_nodes,
                                 desc->known_nodes + desc->known_node_count);
        std::sort(entry.known_nodes.begin(), entry.known_nodes.end(), node_less);
        entry.known_nodes.erase(
            std::unique(entry.known_nodes.begin(), entry.known_nodes.end()),
            entry.known_nodes.end());
    }

    insert_faction_sorted(registry->factions, entry);
    return DOM_FACTION_OK;
}

int dom_faction_get(const dom_faction_registry *registry,
                    dom_faction_id faction_id,
                    dom_faction_info *out_info) {
    int idx;
    if (!registry || !out_info) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    idx = find_faction_index(registry->factions, faction_id);
    if (idx < 0) {
        return DOM_FACTION_NOT_FOUND;
    }
    {
        const FactionEntry &entry = registry->factions[(size_t)idx];
        out_info->faction_id = entry.faction_id;
        out_info->home_scope_kind = entry.home_scope_kind;
        out_info->home_scope_id = entry.home_scope_id;
        out_info->policy_kind = entry.policy_kind;
        out_info->policy_flags = entry.policy_flags;
        out_info->ai_seed = entry.ai_seed;
        out_info->known_node_count = (u32)entry.known_nodes.size();
    }
    return DOM_FACTION_OK;
}

int dom_faction_iterate(const dom_faction_registry *registry,
                        dom_faction_iter_fn fn,
                        void *user) {
    size_t i;
    if (!registry || !fn) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->factions.size(); ++i) {
        const FactionEntry &entry = registry->factions[i];
        dom_faction_info info;
        info.faction_id = entry.faction_id;
        info.home_scope_kind = entry.home_scope_kind;
        info.home_scope_id = entry.home_scope_id;
        info.policy_kind = entry.policy_kind;
        info.policy_flags = entry.policy_flags;
        info.ai_seed = entry.ai_seed;
        info.known_node_count = (u32)entry.known_nodes.size();
        fn(&info, user);
    }
    return DOM_FACTION_OK;
}

u32 dom_faction_count(const dom_faction_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->factions.size();
}

int dom_faction_list_known_nodes(const dom_faction_registry *registry,
                                 dom_faction_id faction_id,
                                 u64 *out_nodes,
                                 u32 max_nodes,
                                 u32 *out_count) {
    int idx;
    u32 count;
    if (!registry || !out_count || faction_id == 0ull) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    idx = find_faction_index(registry->factions, faction_id);
    if (idx < 0) {
        return DOM_FACTION_NOT_FOUND;
    }
    count = (u32)registry->factions[(size_t)idx].known_nodes.size();
    if (out_nodes && max_nodes > 0u) {
        const u32 limit = (count < max_nodes) ? count : max_nodes;
        for (u32 i = 0u; i < limit; ++i) {
            out_nodes[i] = registry->factions[(size_t)idx].known_nodes[i];
        }
    }
    *out_count = count;
    return DOM_FACTION_OK;
}

int dom_faction_resource_get(const dom_faction_registry *registry,
                             dom_faction_id faction_id,
                             dom_resource_id resource_id,
                             i64 *out_quantity) {
    int idx;
    int res_idx;
    if (!registry || !out_quantity || faction_id == 0ull || resource_id == 0ull) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    *out_quantity = 0;
    idx = find_faction_index(registry->factions, faction_id);
    if (idx < 0) {
        return DOM_FACTION_NOT_FOUND;
    }
    res_idx = find_resource_index(registry->factions[(size_t)idx].resources, resource_id);
    if (res_idx < 0) {
        return DOM_FACTION_NOT_FOUND;
    }
    *out_quantity = registry->factions[(size_t)idx].resources[(size_t)res_idx].quantity;
    return DOM_FACTION_OK;
}

int dom_faction_resource_list(const dom_faction_registry *registry,
                              dom_faction_id faction_id,
                              dom_faction_resource_entry *out_entries,
                              u32 max_entries,
                              u32 *out_count) {
    int idx;
    u32 count;
    if (!registry || !out_count || faction_id == 0ull) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    idx = find_faction_index(registry->factions, faction_id);
    if (idx < 0) {
        return DOM_FACTION_NOT_FOUND;
    }
    count = (u32)registry->factions[(size_t)idx].resources.size();
    if (out_entries && max_entries > 0u) {
        const u32 limit = (count < max_entries) ? count : max_entries;
        for (u32 i = 0u; i < limit; ++i) {
            out_entries[i] = registry->factions[(size_t)idx].resources[i];
        }
    }
    *out_count = count;
    return DOM_FACTION_OK;
}

int dom_faction_update_resources(dom_faction_registry *registry,
                                 dom_faction_id faction_id,
                                 const dom_faction_resource_delta *deltas,
                                 u32 delta_count) {
    int idx;
    std::vector<dom_faction_resource_delta> sorted;
    if (!registry || faction_id == 0ull) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    if (delta_count > 0u && !deltas) {
        return DOM_FACTION_INVALID_ARGUMENT;
    }
    idx = find_faction_index(registry->factions, faction_id);
    if (idx < 0) {
        return DOM_FACTION_NOT_FOUND;
    }
    if (delta_count == 0u) {
        return DOM_FACTION_OK;
    }

    sorted.assign(deltas, deltas + delta_count);
    std::sort(sorted.begin(), sorted.end(), delta_less);

    for (u32 i = 0u; i < delta_count; ++i) {
        const dom_faction_resource_delta &delta = sorted[i];
        int res_idx;
        if (delta.resource_id == 0ull) {
            return DOM_FACTION_INVALID_DATA;
        }
        if (delta.delta == 0) {
            continue;
        }
        res_idx = find_resource_index(registry->factions[(size_t)idx].resources,
                                      delta.resource_id);
        if (res_idx < 0) {
            if (delta.delta < 0) {
                return DOM_FACTION_INSUFFICIENT;
            }
            {
                dom_faction_resource_entry entry;
                entry.resource_id = delta.resource_id;
                entry.quantity = delta.delta;
                insert_resource_sorted(registry->factions[(size_t)idx].resources, entry);
            }
            continue;
        }
        {
            std::vector<dom_faction_resource_entry> &res =
                registry->factions[(size_t)idx].resources;
            dom_faction_resource_entry &entry = res[(size_t)res_idx];
            i64 current = entry.quantity;
            i64 next = current + delta.delta;
            if (delta.delta > 0 && current > (LLONG_MAX - delta.delta)) {
                return DOM_FACTION_OVERFLOW;
            }
            if (delta.delta < 0 && current < (LLONG_MIN - delta.delta)) {
                return DOM_FACTION_OVERFLOW;
            }
            if (next < 0) {
                return DOM_FACTION_INSUFFICIENT;
            }
            entry.quantity = next;
            if (entry.quantity == 0) {
                res.erase(res.begin() +
                          (std::vector<dom_faction_resource_entry>::difference_type)res_idx);
            }
        }
    }

    return DOM_FACTION_OK;
}
