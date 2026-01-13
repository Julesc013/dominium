/*
FILE: source/dominium/game/runtime/dom_instrument_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/instrument_registry
RESPONSIBILITY: Deterministic instrument registry (contract bindings).
*/
#include "runtime/dom_instrument_registry.h"

#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct InstrumentEntry {
    dom_instrument_id id_hash;
    u32 kind;
    u64 contract_id_hash;
    std::string id;
    std::string contract_id;
    std::vector<u64> asset_ids;
};

static int find_index(const std::vector<InstrumentEntry> &list, dom_instrument_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id_hash == id_hash) {
            return (int)i;
        }
    }
    return -1;
}

static bool entry_less(const InstrumentEntry &a, const InstrumentEntry &b) {
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static void insert_sorted(std::vector<InstrumentEntry> &list, const InstrumentEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && entry_less(list[i], entry)) {
        ++i;
    }
    while (i < list.size() && !entry_less(entry, list[i])) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<InstrumentEntry>::difference_type)i, entry);
}

static int compute_hash_id(const char *bytes, u32 len, u64 *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_INSTRUMENT_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_INSTRUMENT_INVALID_DATA;
    }
    if (hash == 0ull) {
        return DOM_INSTRUMENT_INVALID_DATA;
    }
    *out_id = hash;
    return DOM_INSTRUMENT_OK;
}

} // namespace

struct dom_instrument_registry {
    std::vector<InstrumentEntry> instruments;
};

dom_instrument_registry *dom_instrument_registry_create(void) {
    return new dom_instrument_registry();
}

void dom_instrument_registry_destroy(dom_instrument_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_instrument_registry_register(dom_instrument_registry *registry,
                                     const dom_instrument_desc *desc) {
    dom_instrument_id id_hash = 0ull;
    u64 contract_hash = 0ull;
    InstrumentEntry entry;
    u32 i;
    if (!registry || !desc) {
        return DOM_INSTRUMENT_INVALID_ARGUMENT;
    }
    if (desc->id && desc->id_len > 0u) {
        int rc = compute_hash_id(desc->id, desc->id_len, &id_hash);
        if (rc != DOM_INSTRUMENT_OK) {
            return rc;
        }
        if (desc->id_hash != 0ull && desc->id_hash != id_hash) {
            return DOM_INSTRUMENT_INVALID_DATA;
        }
    } else {
        id_hash = desc->id_hash;
    }
    if (id_hash == 0ull) {
        return DOM_INSTRUMENT_INVALID_DATA;
    }
    if (desc->contract_id && desc->contract_id_len > 0u) {
        int rc = compute_hash_id(desc->contract_id, desc->contract_id_len, &contract_hash);
        if (rc != DOM_INSTRUMENT_OK) {
            return rc;
        }
        if (desc->contract_id_hash != 0ull && desc->contract_id_hash != contract_hash) {
            return DOM_INSTRUMENT_INVALID_DATA;
        }
    } else {
        contract_hash = desc->contract_id_hash;
    }
    if (contract_hash == 0ull) {
        return DOM_INSTRUMENT_INVALID_DATA;
    }
    if (find_index(registry->instruments, id_hash) >= 0) {
        return DOM_INSTRUMENT_DUPLICATE_ID;
    }
    entry.id_hash = id_hash;
    entry.kind = desc->kind;
    entry.contract_id_hash = contract_hash;
    if (desc->id && desc->id_len > 0u) {
        entry.id.assign(desc->id, desc->id_len);
    }
    if (desc->contract_id && desc->contract_id_len > 0u) {
        entry.contract_id.assign(desc->contract_id, desc->contract_id_len);
    }
    if (desc->asset_ids && desc->asset_id_count > 0u) {
        entry.asset_ids.assign(desc->asset_ids, desc->asset_ids + desc->asset_id_count);
    }
    insert_sorted(registry->instruments, entry);
    return DOM_INSTRUMENT_OK;
}

int dom_instrument_registry_get(const dom_instrument_registry *registry,
                                dom_instrument_id id_hash,
                                dom_instrument_info *out_info) {
    int idx;
    if (!registry || !out_info) {
        return DOM_INSTRUMENT_INVALID_ARGUMENT;
    }
    idx = find_index(registry->instruments, id_hash);
    if (idx < 0) {
        return DOM_INSTRUMENT_NOT_FOUND;
    }
    {
        const InstrumentEntry &entry = registry->instruments[(size_t)idx];
        out_info->id_hash = entry.id_hash;
        out_info->kind = entry.kind;
        out_info->contract_id_hash = entry.contract_id_hash;
        out_info->id = entry.id.empty() ? 0 : entry.id.c_str();
        out_info->id_len = (u32)entry.id.size();
        out_info->contract_id = entry.contract_id.empty() ? 0 : entry.contract_id.c_str();
        out_info->contract_id_len = (u32)entry.contract_id.size();
        out_info->asset_ids = entry.asset_ids.empty() ? 0 : &entry.asset_ids[0];
        out_info->asset_id_count = (u32)entry.asset_ids.size();
    }
    return DOM_INSTRUMENT_OK;
}

int dom_instrument_registry_iterate(const dom_instrument_registry *registry,
                                    dom_instrument_iter_fn fn,
                                    void *user) {
    size_t i;
    if (!registry || !fn) {
        return DOM_INSTRUMENT_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->instruments.size(); ++i) {
        const InstrumentEntry &entry = registry->instruments[i];
        dom_instrument_info info;
        info.id_hash = entry.id_hash;
        info.kind = entry.kind;
        info.contract_id_hash = entry.contract_id_hash;
        info.id = entry.id.empty() ? 0 : entry.id.c_str();
        info.id_len = (u32)entry.id.size();
        info.contract_id = entry.contract_id.empty() ? 0 : entry.contract_id.c_str();
        info.contract_id_len = (u32)entry.contract_id.size();
        info.asset_ids = entry.asset_ids.empty() ? 0 : &entry.asset_ids[0];
        info.asset_id_count = (u32)entry.asset_ids.size();
        fn(&info, user);
    }
    return DOM_INSTRUMENT_OK;
}

u32 dom_instrument_registry_count(const dom_instrument_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->instruments.size();
}
