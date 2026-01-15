/*
FILE: source/dominium/game/runtime/dom_money_standard.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/money_standard
RESPONSIBILITY: Deterministic money standard registry and rendering helpers.
*/
#include "runtime/dom_money_standard.h"

#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct MoneyStandardEntry {
    dom_money_standard_id id_hash;
    u64 base_asset_id_hash;
    u32 denom_scale;
    u32 rounding_mode;
    u64 convert_rule_id_hash;
    std::string id;
    std::string base_asset_id;
    std::string display_name;
    std::string convert_rule_id;
};

static int find_index(const std::vector<MoneyStandardEntry> &list,
                      dom_money_standard_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id_hash == id_hash) {
            return (int)i;
        }
    }
    return -1;
}

static bool entry_less(const MoneyStandardEntry &a, const MoneyStandardEntry &b) {
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static void insert_sorted(std::vector<MoneyStandardEntry> &list,
                          const MoneyStandardEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && entry_less(list[i], entry)) {
        ++i;
    }
    while (i < list.size() && !entry_less(entry, list[i])) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<MoneyStandardEntry>::difference_type)i, entry);
}

static int compute_hash_id(const char *bytes, u32 len, u64 *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_MONEY_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_MONEY_INVALID_DATA;
    }
    if (hash == 0ull) {
        return DOM_MONEY_INVALID_DATA;
    }
    *out_id = hash;
    return DOM_MONEY_OK;
}

} // namespace

struct dom_money_standard_registry {
    std::vector<MoneyStandardEntry> standards;
};

dom_money_standard_registry *dom_money_standard_registry_create(void) {
    return new dom_money_standard_registry();
}

void dom_money_standard_registry_destroy(dom_money_standard_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_money_standard_registry_register(dom_money_standard_registry *registry,
                                         const dom_money_standard_desc *desc) {
    dom_money_standard_id id_hash = 0ull;
    u64 base_hash = 0ull;
    u64 convert_hash = 0ull;
    MoneyStandardEntry entry;
    if (!registry || !desc) {
        return DOM_MONEY_INVALID_ARGUMENT;
    }
    if (desc->id && desc->id_len > 0u) {
        int rc = compute_hash_id(desc->id, desc->id_len, &id_hash);
        if (rc != DOM_MONEY_OK) {
            return rc;
        }
        if (desc->id_hash != 0ull && desc->id_hash != id_hash) {
            return DOM_MONEY_INVALID_DATA;
        }
    } else {
        id_hash = desc->id_hash;
    }
    if (id_hash == 0ull) {
        return DOM_MONEY_INVALID_DATA;
    }
    if (desc->base_asset_id && desc->base_asset_id_len > 0u) {
        int rc = compute_hash_id(desc->base_asset_id, desc->base_asset_id_len, &base_hash);
        if (rc != DOM_MONEY_OK) {
            return rc;
        }
        if (desc->base_asset_id_hash != 0ull && desc->base_asset_id_hash != base_hash) {
            return DOM_MONEY_INVALID_DATA;
        }
    } else {
        base_hash = desc->base_asset_id_hash;
    }
    if (base_hash == 0ull) {
        return DOM_MONEY_INVALID_DATA;
    }
    if (desc->denom_scale == 0u) {
        return DOM_MONEY_INVALID_DATA;
    }
    if (desc->convert_rule_id && desc->convert_rule_id_len > 0u) {
        int rc = compute_hash_id(desc->convert_rule_id, desc->convert_rule_id_len, &convert_hash);
        if (rc != DOM_MONEY_OK) {
            return rc;
        }
        if (desc->convert_rule_id_hash != 0ull && desc->convert_rule_id_hash != convert_hash) {
            return DOM_MONEY_INVALID_DATA;
        }
    } else {
        convert_hash = desc->convert_rule_id_hash;
    }
    if (find_index(registry->standards, id_hash) >= 0) {
        return DOM_MONEY_DUPLICATE_ID;
    }
    entry.id_hash = id_hash;
    entry.base_asset_id_hash = base_hash;
    entry.denom_scale = desc->denom_scale;
    entry.rounding_mode = desc->rounding_mode;
    entry.convert_rule_id_hash = convert_hash;
    if (desc->id && desc->id_len > 0u) {
        entry.id.assign(desc->id, desc->id_len);
    }
    if (desc->base_asset_id && desc->base_asset_id_len > 0u) {
        entry.base_asset_id.assign(desc->base_asset_id, desc->base_asset_id_len);
    }
    if (desc->display_name && desc->display_name_len > 0u) {
        entry.display_name.assign(desc->display_name, desc->display_name_len);
    }
    if (desc->convert_rule_id && desc->convert_rule_id_len > 0u) {
        entry.convert_rule_id.assign(desc->convert_rule_id, desc->convert_rule_id_len);
    }
    insert_sorted(registry->standards, entry);
    return DOM_MONEY_OK;
}

int dom_money_standard_registry_get(const dom_money_standard_registry *registry,
                                    dom_money_standard_id id_hash,
                                    dom_money_standard_info *out_info) {
    int idx;
    if (!registry || !out_info) {
        return DOM_MONEY_INVALID_ARGUMENT;
    }
    idx = find_index(registry->standards, id_hash);
    if (idx < 0) {
        return DOM_MONEY_NOT_FOUND;
    }
    {
        const MoneyStandardEntry &entry = registry->standards[(size_t)idx];
        out_info->id_hash = entry.id_hash;
        out_info->base_asset_id_hash = entry.base_asset_id_hash;
        out_info->denom_scale = entry.denom_scale;
        out_info->rounding_mode = entry.rounding_mode;
        out_info->convert_rule_id_hash = entry.convert_rule_id_hash;
        out_info->id = entry.id.empty() ? 0 : entry.id.c_str();
        out_info->id_len = (u32)entry.id.size();
        out_info->display_name = entry.display_name.empty() ? 0 : entry.display_name.c_str();
        out_info->display_name_len = (u32)entry.display_name.size();
        out_info->convert_rule_id = entry.convert_rule_id.empty() ? 0 : entry.convert_rule_id.c_str();
        out_info->convert_rule_id_len = (u32)entry.convert_rule_id.size();
    }
    return DOM_MONEY_OK;
}

int dom_money_standard_registry_iterate(const dom_money_standard_registry *registry,
                                        dom_money_standard_iter_fn fn,
                                        void *user) {
    size_t i;
    if (!registry || !fn) {
        return DOM_MONEY_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->standards.size(); ++i) {
        const MoneyStandardEntry &entry = registry->standards[i];
        dom_money_standard_info info;
        info.id_hash = entry.id_hash;
        info.base_asset_id_hash = entry.base_asset_id_hash;
        info.denom_scale = entry.denom_scale;
        info.rounding_mode = entry.rounding_mode;
        info.convert_rule_id_hash = entry.convert_rule_id_hash;
        info.id = entry.id.empty() ? 0 : entry.id.c_str();
        info.id_len = (u32)entry.id.size();
        info.display_name = entry.display_name.empty() ? 0 : entry.display_name.c_str();
        info.display_name_len = (u32)entry.display_name.size();
        info.convert_rule_id = entry.convert_rule_id.empty() ? 0 : entry.convert_rule_id.c_str();
        info.convert_rule_id_len = (u32)entry.convert_rule_id.size();
        fn(&info, user);
    }
    return DOM_MONEY_OK;
}

u32 dom_money_standard_registry_count(const dom_money_standard_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->standards.size();
}

int dom_money_standard_render(const dom_money_standard_registry *registry,
                              dom_money_standard_id id_hash,
                              i64 amount,
                              dom_money_rendered *out) {
    dom_money_standard_info info;
    i64 denom;
    if (!registry || !out) {
        return DOM_MONEY_INVALID_ARGUMENT;
    }
    if (dom_money_standard_registry_get(registry, id_hash, &info) != DOM_MONEY_OK) {
        return DOM_MONEY_NOT_FOUND;
    }
    if (info.denom_scale == 0u) {
        return DOM_MONEY_INVALID_DATA;
    }
    denom = (i64)info.denom_scale;
    out->negative = (amount < 0);
    if (amount < 0) {
        amount = -amount;
    }
    out->whole = amount / denom;
    out->minor = (u32)(amount % denom);
    out->scale = info.denom_scale;
    return DOM_MONEY_OK;
}

int dom_money_standard_parse(const dom_money_standard_registry *registry,
                             dom_money_standard_id id_hash,
                             const dom_money_rendered *in,
                             i64 *out_amount) {
    dom_money_standard_info info;
    i64 denom;
    i64 amount;
    if (!registry || !in || !out_amount) {
        return DOM_MONEY_INVALID_ARGUMENT;
    }
    if (dom_money_standard_registry_get(registry, id_hash, &info) != DOM_MONEY_OK) {
        return DOM_MONEY_NOT_FOUND;
    }
    if (info.denom_scale == 0u) {
        return DOM_MONEY_INVALID_DATA;
    }
    denom = (i64)info.denom_scale;
    if (in->scale != info.denom_scale) {
        return DOM_MONEY_INVALID_DATA;
    }
    if ((i64)in->minor >= denom) {
        return DOM_MONEY_INVALID_DATA;
    }
    amount = in->whole * denom + (i64)in->minor;
    if (in->negative) {
        amount = -amount;
    }
    *out_amount = amount;
    return DOM_MONEY_OK;
}
