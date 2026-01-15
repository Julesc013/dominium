/*
FILE: source/dominium/game/runtime/dom_jurisdiction_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/jurisdiction_registry
RESPONSIBILITY: Deterministic jurisdiction economic policy registry.
*/
#include "runtime/dom_jurisdiction_registry.h"

#include <algorithm>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct JurisEntry {
    dom_jurisdiction_policy_desc desc;
    std::string id;
};

static bool entry_less(const JurisEntry &a, const JurisEntry &b) {
    if (a.desc.id_hash != b.desc.id_hash) {
        return a.desc.id_hash < b.desc.id_hash;
    }
    return a.id < b.id;
}

static int compute_hash_id(const char *bytes, u32 len, dom_jurisdiction_id *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_JURIS_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_JURIS_ERR;
    }
    if (hash == 0ull) {
        return DOM_JURIS_ERR;
    }
    *out_id = hash;
    return DOM_JURIS_OK;
}

static JurisEntry *find_entry(std::vector<JurisEntry> &list, dom_jurisdiction_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].desc.id_hash == id_hash) {
            return &list[i];
        }
    }
    return 0;
}

static const JurisEntry *find_entry_const(const std::vector<JurisEntry> &list,
                                          dom_jurisdiction_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].desc.id_hash == id_hash) {
            return &list[i];
        }
    }
    return 0;
}

} // namespace

struct dom_jurisdiction_registry {
    std::vector<JurisEntry> entries;
};

dom_jurisdiction_registry *dom_jurisdiction_registry_create(void) {
    return new dom_jurisdiction_registry();
}

void dom_jurisdiction_registry_destroy(dom_jurisdiction_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_jurisdiction_registry_register(dom_jurisdiction_registry *registry,
                                       const dom_jurisdiction_policy_desc *desc) {
    JurisEntry entry;
    dom_jurisdiction_policy_desc tmp;
    int rc;
    if (!registry || !desc) {
        return DOM_JURIS_INVALID_ARGUMENT;
    }
    tmp = *desc;
    if (tmp.id && tmp.id_len > 0u) {
        rc = compute_hash_id(tmp.id, tmp.id_len, &tmp.id_hash);
        if (rc != DOM_JURIS_OK) {
            return rc;
        }
    }
    if (tmp.id_hash == 0ull) {
        return DOM_JURIS_INVALID_ARGUMENT;
    }
    if (find_entry(registry->entries, tmp.id_hash)) {
        return DOM_JURIS_DUPLICATE_ID;
    }
    entry.desc = tmp;
    entry.id.assign(tmp.id ? tmp.id : "", tmp.id ? tmp.id_len : 0u);
    registry->entries.push_back(entry);
    std::sort(registry->entries.begin(), registry->entries.end(), entry_less);
    return DOM_JURIS_OK;
}

int dom_jurisdiction_registry_get(const dom_jurisdiction_registry *registry,
                                  dom_jurisdiction_id id_hash,
                                  dom_jurisdiction_policy_desc *out_desc) {
    const JurisEntry *entry;
    if (!registry || !out_desc) {
        return DOM_JURIS_INVALID_ARGUMENT;
    }
    entry = find_entry_const(registry->entries, id_hash);
    if (!entry) {
        return DOM_JURIS_NOT_FOUND;
    }
    *out_desc = entry->desc;
    out_desc->id = entry->id.empty() ? 0 : entry->id.c_str();
    out_desc->id_len = (u32)entry->id.size();
    return DOM_JURIS_OK;
}
