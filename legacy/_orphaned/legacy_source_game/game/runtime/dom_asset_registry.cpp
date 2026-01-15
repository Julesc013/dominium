/*
FILE: source/dominium/game/runtime/dom_asset_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/asset_registry
RESPONSIBILITY: Deterministic asset registry (IDs + canonical ordering).
*/
#include "runtime/dom_asset_registry.h"

#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct AssetEntry {
    dom_asset_id id_hash;
    u32 kind;
    u32 unit_scale;
    u32 divisibility;
    u32 provenance_required;
    dom_asset_id issuer_id_hash;
    std::string id;
    std::string display_name;
    std::string issuer_id;
};

static int find_index(const std::vector<AssetEntry> &list, dom_asset_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id_hash == id_hash) {
            return (int)i;
        }
    }
    return -1;
}

static bool entry_less(const AssetEntry &a, const AssetEntry &b) {
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static void insert_sorted(std::vector<AssetEntry> &list, const AssetEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && entry_less(list[i], entry)) {
        ++i;
    }
    while (i < list.size() && !entry_less(entry, list[i])) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<AssetEntry>::difference_type)i, entry);
}

static int compute_hash_id(const char *bytes, u32 len, dom_asset_id *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_ASSET_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_ASSET_INVALID_DATA;
    }
    if (hash == 0ull) {
        return DOM_ASSET_INVALID_DATA;
    }
    *out_id = hash;
    return DOM_ASSET_OK;
}

} // namespace

struct dom_asset_registry {
    std::vector<AssetEntry> assets;
};

dom_asset_registry *dom_asset_registry_create(void) {
    return new dom_asset_registry();
}

void dom_asset_registry_destroy(dom_asset_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_asset_registry_register(dom_asset_registry *registry,
                                const dom_asset_desc *desc) {
    dom_asset_id id_hash = 0ull;
    dom_asset_id issuer_hash = 0ull;
    AssetEntry entry;
    if (!registry || !desc) {
        return DOM_ASSET_INVALID_ARGUMENT;
    }
    if (desc->id && desc->id_len > 0u) {
        int rc = compute_hash_id(desc->id, desc->id_len, &id_hash);
        if (rc != DOM_ASSET_OK) {
            return rc;
        }
        if (desc->id_hash != 0ull && desc->id_hash != id_hash) {
            return DOM_ASSET_INVALID_DATA;
        }
    } else {
        id_hash = desc->id_hash;
    }
    if (id_hash == 0ull) {
        return DOM_ASSET_INVALID_DATA;
    }
    if (desc->unit_scale == 0u) {
        return DOM_ASSET_INVALID_DATA;
    }
    if (desc->divisibility == 0u) {
        return DOM_ASSET_INVALID_DATA;
    }
    if (find_index(registry->assets, id_hash) >= 0) {
        return DOM_ASSET_DUPLICATE_ID;
    }
    if (desc->issuer_id && desc->issuer_id_len > 0u) {
        int rc = compute_hash_id(desc->issuer_id, desc->issuer_id_len, &issuer_hash);
        if (rc != DOM_ASSET_OK) {
            return rc;
        }
        if (desc->issuer_id_hash != 0ull && desc->issuer_id_hash != issuer_hash) {
            return DOM_ASSET_INVALID_DATA;
        }
    } else {
        issuer_hash = desc->issuer_id_hash;
    }

    entry.id_hash = id_hash;
    entry.kind = desc->kind;
    entry.unit_scale = desc->unit_scale;
    entry.divisibility = desc->divisibility;
    entry.provenance_required = desc->provenance_required;
    entry.issuer_id_hash = issuer_hash;
    if (desc->id && desc->id_len > 0u) {
        entry.id.assign(desc->id, desc->id_len);
    }
    if (desc->display_name && desc->display_name_len > 0u) {
        entry.display_name.assign(desc->display_name, desc->display_name_len);
    }
    if (desc->issuer_id && desc->issuer_id_len > 0u) {
        entry.issuer_id.assign(desc->issuer_id, desc->issuer_id_len);
    }
    insert_sorted(registry->assets, entry);
    return DOM_ASSET_OK;
}

int dom_asset_registry_get(const dom_asset_registry *registry,
                           dom_asset_id id_hash,
                           dom_asset_info *out_info) {
    int idx;
    if (!registry || !out_info) {
        return DOM_ASSET_INVALID_ARGUMENT;
    }
    idx = find_index(registry->assets, id_hash);
    if (idx < 0) {
        return DOM_ASSET_NOT_FOUND;
    }
    {
        const AssetEntry &entry = registry->assets[(size_t)idx];
        out_info->id_hash = entry.id_hash;
        out_info->kind = entry.kind;
        out_info->unit_scale = entry.unit_scale;
        out_info->divisibility = entry.divisibility;
        out_info->provenance_required = entry.provenance_required;
        out_info->issuer_id_hash = entry.issuer_id_hash;
        out_info->id = entry.id.empty() ? 0 : entry.id.c_str();
        out_info->id_len = (u32)entry.id.size();
        out_info->display_name = entry.display_name.empty() ? 0 : entry.display_name.c_str();
        out_info->display_name_len = (u32)entry.display_name.size();
        out_info->issuer_id = entry.issuer_id.empty() ? 0 : entry.issuer_id.c_str();
        out_info->issuer_id_len = (u32)entry.issuer_id.size();
    }
    return DOM_ASSET_OK;
}

int dom_asset_registry_iterate(const dom_asset_registry *registry,
                               dom_asset_iter_fn fn,
                               void *user) {
    size_t i;
    if (!registry || !fn) {
        return DOM_ASSET_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->assets.size(); ++i) {
        const AssetEntry &entry = registry->assets[i];
        dom_asset_info info;
        info.id_hash = entry.id_hash;
        info.kind = entry.kind;
        info.unit_scale = entry.unit_scale;
        info.divisibility = entry.divisibility;
        info.provenance_required = entry.provenance_required;
        info.issuer_id_hash = entry.issuer_id_hash;
        info.id = entry.id.empty() ? 0 : entry.id.c_str();
        info.id_len = (u32)entry.id.size();
        info.display_name = entry.display_name.empty() ? 0 : entry.display_name.c_str();
        info.display_name_len = (u32)entry.display_name.size();
        info.issuer_id = entry.issuer_id.empty() ? 0 : entry.issuer_id.c_str();
        info.issuer_id_len = (u32)entry.issuer_id.size();
        fn(&info, user);
    }
    return DOM_ASSET_OK;
}

u32 dom_asset_registry_count(const dom_asset_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->assets.size();
}
