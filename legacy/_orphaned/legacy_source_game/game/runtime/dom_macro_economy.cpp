/*
FILE: source/dominium/game/runtime/dom_macro_economy.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/macro_economy
RESPONSIBILITY: Deterministic macro economy aggregates for system/galaxy scopes.
*/
#include "runtime/dom_macro_economy.h"

#include <vector>
#include <climits>

namespace {

struct MacroScopeEntry {
    u32 scope_kind;
    u64 scope_id;
    u32 flags;
    std::vector<dom_macro_rate_entry> production;
    std::vector<dom_macro_rate_entry> demand;
    std::vector<dom_macro_stock_entry> stockpile;
};

static int find_scope_index(const std::vector<MacroScopeEntry> &list, u64 scope_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].scope_id == scope_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_scope_sorted(std::vector<MacroScopeEntry> &list, const MacroScopeEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].scope_id < entry.scope_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<MacroScopeEntry>::difference_type)i, entry);
}

static int find_rate_index(const std::vector<dom_macro_rate_entry> &list,
                           dom_resource_id resource_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].resource_id == resource_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_rate_sorted(std::vector<dom_macro_rate_entry> &list,
                               const dom_macro_rate_entry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].resource_id < entry.resource_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<dom_macro_rate_entry>::difference_type)i, entry);
}

static int find_stock_index(const std::vector<dom_macro_stock_entry> &list,
                            dom_resource_id resource_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].resource_id == resource_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_stock_sorted(std::vector<dom_macro_stock_entry> &list,
                                const dom_macro_stock_entry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].resource_id < entry.resource_id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<dom_macro_stock_entry>::difference_type)i, entry);
}

static bool scope_kind_valid(u32 scope_kind) {
    return scope_kind == DOM_MACRO_SCOPE_SYSTEM || scope_kind == DOM_MACRO_SCOPE_GALAXY;
}

static std::vector<MacroScopeEntry> *scope_list(dom_macro_economy *econ, u32 scope_kind);
static const std::vector<MacroScopeEntry> *scope_list(const dom_macro_economy *econ, u32 scope_kind);

} // namespace

struct dom_macro_economy {
    std::vector<MacroScopeEntry> systems;
    std::vector<MacroScopeEntry> galaxies;
};

namespace {

static std::vector<MacroScopeEntry> *scope_list(dom_macro_economy *econ, u32 scope_kind) {
    if (!econ) {
        return 0;
    }
    if (scope_kind == DOM_MACRO_SCOPE_SYSTEM) {
        return &econ->systems;
    }
    if (scope_kind == DOM_MACRO_SCOPE_GALAXY) {
        return &econ->galaxies;
    }
    return 0;
}

static const std::vector<MacroScopeEntry> *scope_list(const dom_macro_economy *econ, u32 scope_kind) {
    if (!econ) {
        return 0;
    }
    if (scope_kind == DOM_MACRO_SCOPE_SYSTEM) {
        return &econ->systems;
    }
    if (scope_kind == DOM_MACRO_SCOPE_GALAXY) {
        return &econ->galaxies;
    }
    return 0;
}

static int ensure_scope(dom_macro_economy *econ, u32 scope_kind, u64 scope_id) {
    std::vector<MacroScopeEntry> *list;
    MacroScopeEntry entry;
    if (!econ || scope_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    if (find_scope_index(*list, scope_id) >= 0) {
        return DOM_MACRO_ECONOMY_OK;
    }
    entry.scope_kind = scope_kind;
    entry.scope_id = scope_id;
    entry.flags = 0u;
    entry.production.clear();
    entry.demand.clear();
    entry.stockpile.clear();
    insert_scope_sorted(*list, entry);
    return DOM_MACRO_ECONOMY_OK;
}

} // namespace

dom_macro_economy *dom_macro_economy_create(void) {
    dom_macro_economy *econ = new dom_macro_economy();
    if (!econ) {
        return 0;
    }
    (void)dom_macro_economy_init(econ);
    return econ;
}

void dom_macro_economy_destroy(dom_macro_economy *econ) {
    if (!econ) {
        return;
    }
    delete econ;
}

int dom_macro_economy_init(dom_macro_economy *econ) {
    if (!econ) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    econ->systems.clear();
    econ->galaxies.clear();
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_register_system(dom_macro_economy *econ, u64 system_id) {
    if (!econ || system_id == 0ull) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    if (find_scope_index(econ->systems, system_id) >= 0) {
        return DOM_MACRO_ECONOMY_DUPLICATE_ID;
    }
    return ensure_scope(econ, DOM_MACRO_SCOPE_SYSTEM, system_id);
}

int dom_macro_economy_register_galaxy(dom_macro_economy *econ, u64 galaxy_id) {
    if (!econ || galaxy_id == 0ull) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    if (find_scope_index(econ->galaxies, galaxy_id) >= 0) {
        return DOM_MACRO_ECONOMY_DUPLICATE_ID;
    }
    return ensure_scope(econ, DOM_MACRO_SCOPE_GALAXY, galaxy_id);
}

int dom_macro_economy_get_scope(const dom_macro_economy *econ,
                                u32 scope_kind,
                                u64 scope_id,
                                dom_macro_scope_info *out_info) {
    const std::vector<MacroScopeEntry> *list;
    int idx;
    if (!econ || !out_info || scope_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    {
        const MacroScopeEntry &entry = (*list)[(size_t)idx];
        out_info->scope_kind = entry.scope_kind;
        out_info->scope_id = entry.scope_id;
        out_info->flags = entry.flags;
        out_info->production_count = (u32)entry.production.size();
        out_info->demand_count = (u32)entry.demand.size();
        out_info->stockpile_count = (u32)entry.stockpile.size();
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_list_scopes(const dom_macro_economy *econ,
                                  u32 scope_kind,
                                  dom_macro_scope_info *out_infos,
                                  u32 max_infos,
                                  u32 *out_count) {
    const std::vector<MacroScopeEntry> *list;
    if (!econ || !out_count || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    *out_count = (u32)list->size();
    if (out_infos && max_infos > 0u) {
        const u32 limit = (*out_count < max_infos) ? *out_count : max_infos;
        for (u32 i = 0u; i < limit; ++i) {
            const MacroScopeEntry &entry = (*list)[i];
            out_infos[i].scope_kind = entry.scope_kind;
            out_infos[i].scope_id = entry.scope_id;
            out_infos[i].flags = entry.flags;
            out_infos[i].production_count = (u32)entry.production.size();
            out_infos[i].demand_count = (u32)entry.demand.size();
            out_infos[i].stockpile_count = (u32)entry.stockpile.size();
        }
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_iterate(const dom_macro_economy *econ,
                              u32 scope_kind,
                              dom_macro_scope_iter_fn fn,
                              void *user) {
    const std::vector<MacroScopeEntry> *list;
    size_t i;
    if (!econ || !fn || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    for (i = 0u; i < list->size(); ++i) {
        const MacroScopeEntry &entry = (*list)[i];
        dom_macro_scope_info info;
        info.scope_kind = entry.scope_kind;
        info.scope_id = entry.scope_id;
        info.flags = entry.flags;
        info.production_count = (u32)entry.production.size();
        info.demand_count = (u32)entry.demand.size();
        info.stockpile_count = (u32)entry.stockpile.size();
        fn(&info, user);
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_rate_get(const dom_macro_economy *econ,
                               u32 scope_kind,
                               u64 scope_id,
                               dom_resource_id resource_id,
                               i64 *out_production_rate,
                               i64 *out_demand_rate) {
    const std::vector<MacroScopeEntry> *list;
    int idx;
    if (!econ || scope_id == 0ull || resource_id == 0ull ||
        !out_production_rate || !out_demand_rate || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    {
        const MacroScopeEntry &entry = (*list)[(size_t)idx];
        int pidx = find_rate_index(entry.production, resource_id);
        int didx = find_rate_index(entry.demand, resource_id);
        *out_production_rate = (pidx >= 0) ? entry.production[(size_t)pidx].rate_per_tick : 0;
        *out_demand_rate = (didx >= 0) ? entry.demand[(size_t)didx].rate_per_tick : 0;
    }
    return DOM_MACRO_ECONOMY_OK;
}

static int update_rate_list(std::vector<dom_macro_rate_entry> &list,
                            dom_resource_id resource_id,
                            i64 new_rate) {
    int idx = find_rate_index(list, resource_id);
    if (new_rate == 0) {
        if (idx >= 0) {
            list.erase(list.begin() + (std::vector<dom_macro_rate_entry>::difference_type)idx);
        }
        return DOM_MACRO_ECONOMY_OK;
    }
    if (idx >= 0) {
        list[(size_t)idx].rate_per_tick = new_rate;
        return DOM_MACRO_ECONOMY_OK;
    }
    {
        dom_macro_rate_entry entry;
        entry.resource_id = resource_id;
        entry.rate_per_tick = new_rate;
        insert_rate_sorted(list, entry);
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_rate_set(dom_macro_economy *econ,
                               u32 scope_kind,
                               u64 scope_id,
                               dom_resource_id resource_id,
                               i64 production_rate,
                               i64 demand_rate) {
    std::vector<MacroScopeEntry> *list;
    int idx;
    if (!econ || scope_id == 0ull || resource_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    if (ensure_scope(econ, scope_kind, scope_id) != DOM_MACRO_ECONOMY_OK) {
        return DOM_MACRO_ECONOMY_ERR;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_ERR;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    {
        MacroScopeEntry &entry = (*list)[(size_t)idx];
        (void)update_rate_list(entry.production, resource_id, production_rate);
        (void)update_rate_list(entry.demand, resource_id, demand_rate);
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_rate_delta(dom_macro_economy *econ,
                                 u32 scope_kind,
                                 u64 scope_id,
                                 dom_resource_id resource_id,
                                 i64 production_delta,
                                 i64 demand_delta) {
    i64 prod = 0;
    i64 dem = 0;
    int rc;
    if (!econ || scope_id == 0ull || resource_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    rc = dom_macro_economy_rate_get(econ, scope_kind, scope_id, resource_id, &prod, &dem);
    if (rc == DOM_MACRO_ECONOMY_NOT_FOUND) {
        prod = 0;
        dem = 0;
    } else if (rc != DOM_MACRO_ECONOMY_OK) {
        return rc;
    }
    if ((production_delta > 0 && prod > LLONG_MAX - production_delta) ||
        (production_delta < 0 && prod < LLONG_MIN - production_delta) ||
        (demand_delta > 0 && dem > LLONG_MAX - demand_delta) ||
        (demand_delta < 0 && dem < LLONG_MIN - demand_delta)) {
        return DOM_MACRO_ECONOMY_OVERFLOW;
    }
    prod += production_delta;
    dem += demand_delta;
    return dom_macro_economy_rate_set(econ, scope_kind, scope_id, resource_id, prod, dem);
}

int dom_macro_economy_list_production(const dom_macro_economy *econ,
                                      u32 scope_kind,
                                      u64 scope_id,
                                      dom_macro_rate_entry *out_entries,
                                      u32 max_entries,
                                      u32 *out_count) {
    const std::vector<MacroScopeEntry> *list;
    int idx;
    if (!econ || !out_count || scope_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    {
        const MacroScopeEntry &entry = (*list)[(size_t)idx];
        u32 count = (u32)entry.production.size();
        if (out_entries && max_entries > 0u) {
            const u32 limit = (count < max_entries) ? count : max_entries;
            for (u32 i = 0u; i < limit; ++i) {
                out_entries[i] = entry.production[i];
            }
        }
        *out_count = count;
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_list_demand(const dom_macro_economy *econ,
                                  u32 scope_kind,
                                  u64 scope_id,
                                  dom_macro_rate_entry *out_entries,
                                  u32 max_entries,
                                  u32 *out_count) {
    const std::vector<MacroScopeEntry> *list;
    int idx;
    if (!econ || !out_count || scope_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    {
        const MacroScopeEntry &entry = (*list)[(size_t)idx];
        u32 count = (u32)entry.demand.size();
        if (out_entries && max_entries > 0u) {
            const u32 limit = (count < max_entries) ? count : max_entries;
            for (u32 i = 0u; i < limit; ++i) {
                out_entries[i] = entry.demand[i];
            }
        }
        *out_count = count;
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_stockpile_get(const dom_macro_economy *econ,
                                    u32 scope_kind,
                                    u64 scope_id,
                                    dom_resource_id resource_id,
                                    i64 *out_quantity) {
    const std::vector<MacroScopeEntry> *list;
    int idx;
    int sidx;
    if (!econ || !out_quantity || scope_id == 0ull || resource_id == 0ull ||
        !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    sidx = find_stock_index((*list)[(size_t)idx].stockpile, resource_id);
    if (sidx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    *out_quantity = (*list)[(size_t)idx].stockpile[(size_t)sidx].quantity;
    return DOM_MACRO_ECONOMY_OK;
}

static int update_stock_list(std::vector<dom_macro_stock_entry> &list,
                             dom_resource_id resource_id,
                             i64 quantity) {
    int idx = find_stock_index(list, resource_id);
    if (quantity == 0) {
        if (idx >= 0) {
            list.erase(list.begin() + (std::vector<dom_macro_stock_entry>::difference_type)idx);
        }
        return DOM_MACRO_ECONOMY_OK;
    }
    if (idx >= 0) {
        list[(size_t)idx].quantity = quantity;
        return DOM_MACRO_ECONOMY_OK;
    }
    {
        dom_macro_stock_entry entry;
        entry.resource_id = resource_id;
        entry.quantity = quantity;
        insert_stock_sorted(list, entry);
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_stockpile_set(dom_macro_economy *econ,
                                    u32 scope_kind,
                                    u64 scope_id,
                                    dom_resource_id resource_id,
                                    i64 quantity) {
    std::vector<MacroScopeEntry> *list;
    int idx;
    if (!econ || scope_id == 0ull || resource_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    if (ensure_scope(econ, scope_kind, scope_id) != DOM_MACRO_ECONOMY_OK) {
        return DOM_MACRO_ECONOMY_ERR;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_ERR;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    return update_stock_list((*list)[(size_t)idx].stockpile, resource_id, quantity);
}

int dom_macro_economy_stockpile_delta(dom_macro_economy *econ,
                                      u32 scope_kind,
                                      u64 scope_id,
                                      dom_resource_id resource_id,
                                      i64 delta) {
    i64 qty = 0;
    int rc;
    if (!econ || scope_id == 0ull || resource_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    rc = dom_macro_economy_stockpile_get(econ, scope_kind, scope_id, resource_id, &qty);
    if (rc == DOM_MACRO_ECONOMY_NOT_FOUND) {
        qty = 0;
    } else if (rc != DOM_MACRO_ECONOMY_OK) {
        return rc;
    }
    if ((delta > 0 && qty > LLONG_MAX - delta) ||
        (delta < 0 && qty < LLONG_MIN - delta)) {
        return DOM_MACRO_ECONOMY_OVERFLOW;
    }
    qty += delta;
    return dom_macro_economy_stockpile_set(econ, scope_kind, scope_id, resource_id, qty);
}

int dom_macro_economy_list_stockpile(const dom_macro_economy *econ,
                                     u32 scope_kind,
                                     u64 scope_id,
                                     dom_macro_stock_entry *out_entries,
                                     u32 max_entries,
                                     u32 *out_count) {
    const std::vector<MacroScopeEntry> *list;
    int idx;
    if (!econ || !out_count || scope_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    {
        const MacroScopeEntry &entry = (*list)[(size_t)idx];
        u32 count = (u32)entry.stockpile.size();
        if (out_entries && max_entries > 0u) {
            const u32 limit = (count < max_entries) ? count : max_entries;
            for (u32 i = 0u; i < limit; ++i) {
                out_entries[i] = entry.stockpile[i];
            }
        }
        *out_count = count;
    }
    return DOM_MACRO_ECONOMY_OK;
}

int dom_macro_economy_flags_apply(dom_macro_economy *econ,
                                  u32 scope_kind,
                                  u64 scope_id,
                                  u32 flags_set,
                                  u32 flags_clear) {
    std::vector<MacroScopeEntry> *list;
    int idx;
    if (!econ || scope_id == 0ull || !scope_kind_valid(scope_kind)) {
        return DOM_MACRO_ECONOMY_INVALID_ARGUMENT;
    }
    if (ensure_scope(econ, scope_kind, scope_id) != DOM_MACRO_ECONOMY_OK) {
        return DOM_MACRO_ECONOMY_ERR;
    }
    list = scope_list(econ, scope_kind);
    if (!list) {
        return DOM_MACRO_ECONOMY_ERR;
    }
    idx = find_scope_index(*list, scope_id);
    if (idx < 0) {
        return DOM_MACRO_ECONOMY_NOT_FOUND;
    }
    {
        MacroScopeEntry &entry = (*list)[(size_t)idx];
        entry.flags |= flags_set;
        entry.flags &= ~flags_clear;
    }
    return DOM_MACRO_ECONOMY_OK;
}
