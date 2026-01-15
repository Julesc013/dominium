/*
FILE: source/dominium/game/runtime/dom_contract_templates.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/contract_templates
RESPONSIBILITY: Deterministic contract template registry (obligation schedules).
*/
#include "runtime/dom_contract_templates.h"

#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct ContractTemplateEntry {
    dom_contract_template_id id_hash;
    std::string id;
    std::vector<dom_contract_obligation> obligations;
};

static int find_index(const std::vector<ContractTemplateEntry> &list,
                      dom_contract_template_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id_hash == id_hash) {
            return (int)i;
        }
    }
    return -1;
}

static bool entry_less(const ContractTemplateEntry &a, const ContractTemplateEntry &b) {
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static void insert_sorted(std::vector<ContractTemplateEntry> &list,
                          const ContractTemplateEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && entry_less(list[i], entry)) {
        ++i;
    }
    while (i < list.size() && !entry_less(entry, list[i])) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<ContractTemplateEntry>::difference_type)i, entry);
}

static int compute_hash_id(const char *bytes, u32 len, u64 *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_CONTRACT_TEMPLATE_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
    }
    if (hash == 0ull) {
        return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
    }
    *out_id = hash;
    return DOM_CONTRACT_TEMPLATE_OK;
}

static int fill_obligation(const dom_contract_obligation_desc &src,
                           dom_contract_obligation &dst) {
    dom_contract_role_id from_hash = 0ull;
    dom_contract_role_id to_hash = 0ull;
    u64 asset_hash = 0ull;

    dst = dom_contract_obligation();
    dst.amount = src.amount;
    dst.offset_ticks = src.offset_ticks;

    if (src.role_from_id && src.role_from_id_len > 0u) {
        int rc = compute_hash_id(src.role_from_id, src.role_from_id_len, &from_hash);
        if (rc != DOM_CONTRACT_TEMPLATE_OK) {
            return rc;
        }
        if (src.role_from_hash != 0ull && src.role_from_hash != from_hash) {
            return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
        }
        dst.role_from_id = src.role_from_id;
        dst.role_from_id_len = src.role_from_id_len;
    } else {
        from_hash = src.role_from_hash;
    }
    if (from_hash == 0ull) {
        return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
    }

    if (src.role_to_id && src.role_to_id_len > 0u) {
        int rc = compute_hash_id(src.role_to_id, src.role_to_id_len, &to_hash);
        if (rc != DOM_CONTRACT_TEMPLATE_OK) {
            return rc;
        }
        if (src.role_to_hash != 0ull && src.role_to_hash != to_hash) {
            return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
        }
        dst.role_to_id = src.role_to_id;
        dst.role_to_id_len = src.role_to_id_len;
    } else {
        to_hash = src.role_to_hash;
    }
    if (to_hash == 0ull) {
        return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
    }

    if (src.asset_id && src.asset_id_len > 0u) {
        int rc = compute_hash_id(src.asset_id, src.asset_id_len, &asset_hash);
        if (rc != DOM_CONTRACT_TEMPLATE_OK) {
            return rc;
        }
        if (src.asset_id_hash != 0ull && src.asset_id_hash != asset_hash) {
            return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
        }
        dst.asset_id = src.asset_id;
        dst.asset_id_len = src.asset_id_len;
    } else {
        asset_hash = src.asset_id_hash;
    }
    if (asset_hash == 0ull) {
        return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
    }

    dst.role_from_hash = from_hash;
    dst.role_to_hash = to_hash;
    dst.asset_id_hash = asset_hash;
    return DOM_CONTRACT_TEMPLATE_OK;
}

} // namespace

struct dom_contract_template_registry {
    std::vector<ContractTemplateEntry> templates;
};

dom_contract_template_registry *dom_contract_template_registry_create(void) {
    return new dom_contract_template_registry();
}

void dom_contract_template_registry_destroy(dom_contract_template_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_contract_template_registry_register(dom_contract_template_registry *registry,
                                            const dom_contract_template_desc *desc) {
    dom_contract_template_id id_hash = 0ull;
    ContractTemplateEntry entry;
    u32 i;
    if (!registry || !desc) {
        return DOM_CONTRACT_TEMPLATE_INVALID_ARGUMENT;
    }
    if (desc->id && desc->id_len > 0u) {
        int rc = compute_hash_id(desc->id, desc->id_len, &id_hash);
        if (rc != DOM_CONTRACT_TEMPLATE_OK) {
            return rc;
        }
        if (desc->id_hash != 0ull && desc->id_hash != id_hash) {
            return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
        }
    } else {
        id_hash = desc->id_hash;
    }
    if (id_hash == 0ull) {
        return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
    }
    if (find_index(registry->templates, id_hash) >= 0) {
        return DOM_CONTRACT_TEMPLATE_DUPLICATE_ID;
    }
    if (!desc->obligations || desc->obligation_count == 0u) {
        return DOM_CONTRACT_TEMPLATE_INVALID_DATA;
    }
    entry.id_hash = id_hash;
    if (desc->id && desc->id_len > 0u) {
        entry.id.assign(desc->id, desc->id_len);
    }
    entry.obligations.reserve(desc->obligation_count);
    for (i = 0u; i < desc->obligation_count; ++i) {
        dom_contract_obligation obligation;
        int rc = fill_obligation(desc->obligations[i], obligation);
        if (rc != DOM_CONTRACT_TEMPLATE_OK) {
            return rc;
        }
        entry.obligations.push_back(obligation);
    }
    insert_sorted(registry->templates, entry);
    return DOM_CONTRACT_TEMPLATE_OK;
}

int dom_contract_template_registry_get(const dom_contract_template_registry *registry,
                                       dom_contract_template_id id_hash,
                                       dom_contract_template_info *out_info) {
    int idx;
    if (!registry || !out_info) {
        return DOM_CONTRACT_TEMPLATE_INVALID_ARGUMENT;
    }
    idx = find_index(registry->templates, id_hash);
    if (idx < 0) {
        return DOM_CONTRACT_TEMPLATE_NOT_FOUND;
    }
    {
        const ContractTemplateEntry &entry = registry->templates[(size_t)idx];
        out_info->id_hash = entry.id_hash;
        out_info->id = entry.id.empty() ? 0 : entry.id.c_str();
        out_info->id_len = (u32)entry.id.size();
        out_info->obligations = entry.obligations.empty() ? 0 : &entry.obligations[0];
        out_info->obligation_count = (u32)entry.obligations.size();
    }
    return DOM_CONTRACT_TEMPLATE_OK;
}

int dom_contract_template_registry_iterate(const dom_contract_template_registry *registry,
                                           dom_contract_template_iter_fn fn,
                                           void *user) {
    size_t i;
    if (!registry || !fn) {
        return DOM_CONTRACT_TEMPLATE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->templates.size(); ++i) {
        const ContractTemplateEntry &entry = registry->templates[i];
        dom_contract_template_info info;
        info.id_hash = entry.id_hash;
        info.id = entry.id.empty() ? 0 : entry.id.c_str();
        info.id_len = (u32)entry.id.size();
        info.obligations = entry.obligations.empty() ? 0 : &entry.obligations[0];
        info.obligation_count = (u32)entry.obligations.size();
        fn(&info, user);
    }
    return DOM_CONTRACT_TEMPLATE_OK;
}

u32 dom_contract_template_registry_count(const dom_contract_template_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->templates.size();
}
