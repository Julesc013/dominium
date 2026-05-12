/*
FILE: source/dominium/game/runtime/dom_station_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/station_registry
RESPONSIBILITY: Deterministic station registry + inventory storage.
*/
#include "runtime/dom_station_registry.h"

#include <algorithm>
#include <vector>
#include <climits>

namespace {

struct StationEntry {
    dom_station_id station_id;
    dom_body_id body_id;
    dom_frame_id frame_id;
    std::vector<dom_inventory_entry> inventory;
};

static int find_station_index(const std::vector<StationEntry> &list,
                              dom_station_id station_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].station_id == station_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_station_sorted(std::vector<StationEntry> &list,
                                  const StationEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].station_id < entry.station_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<StationEntry>::difference_type)i, entry);
}

static bool inventory_less(const dom_inventory_entry &a,
                           const dom_inventory_entry &b) {
    return a.resource_id < b.resource_id;
}

static int find_inventory_index(const std::vector<dom_inventory_entry> &list,
                                dom_resource_id resource_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].resource_id == resource_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_inventory_sorted(std::vector<dom_inventory_entry> &list,
                                    const dom_inventory_entry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].resource_id < entry.resource_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<dom_inventory_entry>::difference_type)i, entry);
}

} // namespace

struct dom_station_registry {
    std::vector<StationEntry> stations;
};

dom_station_registry *dom_station_registry_create(void) {
    dom_station_registry *registry = new dom_station_registry();
    if (!registry) {
        return 0;
    }
    (void)dom_station_registry_init(registry);
    return registry;
}

void dom_station_registry_destroy(dom_station_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_station_registry_init(dom_station_registry *registry) {
    if (!registry) {
        return DOM_STATION_REGISTRY_INVALID_ARGUMENT;
    }
    registry->stations.clear();
    return DOM_STATION_REGISTRY_OK;
}

int dom_station_register(dom_station_registry *registry,
                         const dom_station_desc *desc) {
    StationEntry entry;
    if (!registry || !desc) {
        return DOM_STATION_REGISTRY_INVALID_ARGUMENT;
    }
    if (desc->station_id == 0ull || desc->body_id == 0ull) {
        return DOM_STATION_REGISTRY_INVALID_DATA;
    }
    if (find_station_index(registry->stations, desc->station_id) >= 0) {
        return DOM_STATION_REGISTRY_DUPLICATE_ID;
    }
    entry.station_id = desc->station_id;
    entry.body_id = desc->body_id;
    entry.frame_id = desc->frame_id;
    entry.inventory.clear();
    insert_station_sorted(registry->stations, entry);
    return DOM_STATION_REGISTRY_OK;
}

int dom_station_get(const dom_station_registry *registry,
                    dom_station_id station_id,
                    dom_station_info *out_info) {
    int idx;
    if (!registry || !out_info) {
        return DOM_STATION_REGISTRY_INVALID_ARGUMENT;
    }
    idx = find_station_index(registry->stations, station_id);
    if (idx < 0) {
        return DOM_STATION_REGISTRY_NOT_FOUND;
    }
    {
        const StationEntry &entry = registry->stations[(size_t)idx];
        out_info->station_id = entry.station_id;
        out_info->body_id = entry.body_id;
        out_info->frame_id = entry.frame_id;
    }
    return DOM_STATION_REGISTRY_OK;
}

int dom_station_iterate(const dom_station_registry *registry,
                        dom_station_iter_fn fn,
                        void *user) {
    size_t i;
    if (!registry || !fn) {
        return DOM_STATION_REGISTRY_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->stations.size(); ++i) {
        const StationEntry &entry = registry->stations[i];
        dom_station_info info;
        info.station_id = entry.station_id;
        info.body_id = entry.body_id;
        info.frame_id = entry.frame_id;
        fn(&info, user);
    }
    return DOM_STATION_REGISTRY_OK;
}

u32 dom_station_count(const dom_station_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->stations.size();
}

int dom_station_inventory_get(const dom_station_registry *registry,
                              dom_station_id station_id,
                              dom_resource_id resource_id,
                              i64 *out_quantity) {
    int idx;
    int inv_idx;
    if (!registry || !out_quantity || station_id == 0ull || resource_id == 0ull) {
        return DOM_STATION_REGISTRY_INVALID_ARGUMENT;
    }
    *out_quantity = 0;
    idx = find_station_index(registry->stations, station_id);
    if (idx < 0) {
        return DOM_STATION_REGISTRY_NOT_FOUND;
    }
    inv_idx = find_inventory_index(registry->stations[(size_t)idx].inventory, resource_id);
    if (inv_idx < 0) {
        return DOM_STATION_REGISTRY_NOT_FOUND;
    }
    *out_quantity = registry->stations[(size_t)idx].inventory[(size_t)inv_idx].quantity;
    return DOM_STATION_REGISTRY_OK;
}

int dom_station_inventory_add(dom_station_registry *registry,
                              dom_station_id station_id,
                              dom_resource_id resource_id,
                              i64 amount) {
    int idx;
    int inv_idx;
    if (!registry || station_id == 0ull || resource_id == 0ull) {
        return DOM_STATION_REGISTRY_INVALID_ARGUMENT;
    }
    if (amount <= 0) {
        return DOM_STATION_REGISTRY_INVALID_DATA;
    }
    idx = find_station_index(registry->stations, station_id);
    if (idx < 0) {
        return DOM_STATION_REGISTRY_NOT_FOUND;
    }
    inv_idx = find_inventory_index(registry->stations[(size_t)idx].inventory, resource_id);
    if (inv_idx >= 0) {
        i64 current = registry->stations[(size_t)idx].inventory[(size_t)inv_idx].quantity;
        if (current > (LLONG_MAX - amount)) {
            return DOM_STATION_REGISTRY_OVERFLOW;
        }
        registry->stations[(size_t)idx].inventory[(size_t)inv_idx].quantity = current + amount;
        return DOM_STATION_REGISTRY_OK;
    }
    {
        dom_inventory_entry entry;
        entry.resource_id = resource_id;
        entry.quantity = amount;
        insert_inventory_sorted(registry->stations[(size_t)idx].inventory, entry);
    }
    return DOM_STATION_REGISTRY_OK;
}

int dom_station_inventory_remove(dom_station_registry *registry,
                                 dom_station_id station_id,
                                 dom_resource_id resource_id,
                                 i64 amount) {
    int idx;
    int inv_idx;
    if (!registry || station_id == 0ull || resource_id == 0ull) {
        return DOM_STATION_REGISTRY_INVALID_ARGUMENT;
    }
    if (amount <= 0) {
        return DOM_STATION_REGISTRY_INVALID_DATA;
    }
    idx = find_station_index(registry->stations, station_id);
    if (idx < 0) {
        return DOM_STATION_REGISTRY_NOT_FOUND;
    }
    inv_idx = find_inventory_index(registry->stations[(size_t)idx].inventory, resource_id);
    if (inv_idx < 0) {
        return DOM_STATION_REGISTRY_INSUFFICIENT;
    }
    {
        std::vector<dom_inventory_entry> &inv = registry->stations[(size_t)idx].inventory;
        dom_inventory_entry &entry = inv[(size_t)inv_idx];
        if (entry.quantity < amount) {
            return DOM_STATION_REGISTRY_INSUFFICIENT;
        }
        entry.quantity -= amount;
        if (entry.quantity == 0) {
            inv.erase(inv.begin() + (std::vector<dom_inventory_entry>::difference_type)inv_idx);
        }
    }
    return DOM_STATION_REGISTRY_OK;
}

int dom_station_inventory_list(const dom_station_registry *registry,
                               dom_station_id station_id,
                               dom_inventory_entry *out_entries,
                               u32 max_entries,
                               u32 *out_count) {
    int idx;
    u32 count;
    if (!registry || !out_count || station_id == 0ull) {
        return DOM_STATION_REGISTRY_INVALID_ARGUMENT;
    }
    idx = find_station_index(registry->stations, station_id);
    if (idx < 0) {
        return DOM_STATION_REGISTRY_NOT_FOUND;
    }
    count = (u32)registry->stations[(size_t)idx].inventory.size();
    if (out_entries && max_entries > 0u) {
        const u32 limit = (count < max_entries) ? count : max_entries;
        for (u32 i = 0u; i < limit; ++i) {
            out_entries[i] = registry->stations[(size_t)idx].inventory[i];
        }
    }
    *out_count = count;
    return DOM_STATION_REGISTRY_OK;
}
