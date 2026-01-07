/*
FILE: source/dominium/game/runtime/dom_body_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/body_registry
RESPONSIBILITY: Deterministic body registry (IDs + baseline constants).
*/
#include "runtime/dom_body_registry.h"

#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct BodyEntry {
    dom_body_id id;
    dom_system_id system_id;
    u32 kind;
    q48_16 radius_m;
    u64 mu_m3_s2;
    u64 rotation_period_ticks;
    u64 rotation_epoch_tick;
    q16_16 axial_tilt_turns;
    u8 has_axial_tilt;
    std::string string_id;
};

static int find_index(const std::vector<BodyEntry> &list, dom_body_id id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_sorted(std::vector<BodyEntry> &list, const BodyEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && list[i].id < entry.id) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<BodyEntry>::difference_type)i, entry);
}

static int compute_hash_id(const char *bytes, u32 len, dom_body_id *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_BODY_REGISTRY_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_BODY_REGISTRY_INVALID_DATA;
    }
    if (hash == 0ull) {
        return DOM_BODY_REGISTRY_INVALID_DATA;
    }
    *out_id = hash;
    return DOM_BODY_REGISTRY_OK;
}

static int validate_body_desc(const dom_body_desc *desc) {
    if (!desc) {
        return DOM_BODY_REGISTRY_INVALID_ARGUMENT;
    }
    if (desc->system_id == 0ull) {
        return DOM_BODY_REGISTRY_INVALID_DATA;
    }
    if (desc->kind < DOM_BODY_KIND_STAR || desc->kind > DOM_BODY_KIND_STATION) {
        return DOM_BODY_REGISTRY_INVALID_DATA;
    }
    if (desc->radius_m <= 0) {
        return DOM_BODY_REGISTRY_INVALID_DATA;
    }
    if (desc->mu_m3_s2 == 0ull) {
        return DOM_BODY_REGISTRY_INVALID_DATA;
    }
    if (desc->has_axial_tilt) {
        if (desc->axial_tilt_turns < 0) {
            return DOM_BODY_REGISTRY_INVALID_DATA;
        }
        if ((u32)desc->axial_tilt_turns > 0x8000u) {
            return DOM_BODY_REGISTRY_INVALID_DATA;
        }
    }
    return DOM_BODY_REGISTRY_OK;
}

} // namespace

struct dom_body_registry {
    std::vector<BodyEntry> bodies;
};

dom_body_registry *dom_body_registry_create(void) {
    return new dom_body_registry();
}

void dom_body_registry_destroy(dom_body_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_body_registry_register(dom_body_registry *registry,
                               const dom_body_desc *desc) {
    dom_body_id id = 0ull;
    BodyEntry entry;
    int rc;
    if (!registry || !desc) {
        return DOM_BODY_REGISTRY_INVALID_ARGUMENT;
    }
    rc = validate_body_desc(desc);
    if (rc != DOM_BODY_REGISTRY_OK) {
        return rc;
    }
    if (desc->string_id && desc->string_id_len > 0u) {
        rc = compute_hash_id(desc->string_id, desc->string_id_len, &id);
        if (rc != DOM_BODY_REGISTRY_OK) {
            return rc;
        }
        if (desc->id != 0ull && desc->id != id) {
            return DOM_BODY_REGISTRY_INVALID_DATA;
        }
    } else {
        id = desc->id;
    }
    if (id == 0ull) {
        return DOM_BODY_REGISTRY_INVALID_DATA;
    }
    if (find_index(registry->bodies, id) >= 0) {
        return DOM_BODY_REGISTRY_DUPLICATE_ID;
    }
    entry.id = id;
    entry.system_id = desc->system_id;
    entry.kind = desc->kind;
    entry.radius_m = desc->radius_m;
    entry.mu_m3_s2 = desc->mu_m3_s2;
    entry.rotation_period_ticks = desc->rotation_period_ticks;
    entry.rotation_epoch_tick = desc->rotation_epoch_tick;
    entry.axial_tilt_turns = desc->axial_tilt_turns;
    entry.has_axial_tilt = desc->has_axial_tilt;
    if (desc->string_id && desc->string_id_len > 0u) {
        entry.string_id.assign(desc->string_id, desc->string_id_len);
    } else {
        entry.string_id.clear();
    }
    insert_sorted(registry->bodies, entry);
    return DOM_BODY_REGISTRY_OK;
}

int dom_body_registry_get(const dom_body_registry *registry,
                          dom_body_id id,
                          dom_body_info *out_info) {
    int idx;
    if (!registry || !out_info) {
        return DOM_BODY_REGISTRY_INVALID_ARGUMENT;
    }
    idx = find_index(registry->bodies, id);
    if (idx < 0) {
        return DOM_BODY_REGISTRY_NOT_FOUND;
    }
    {
        const BodyEntry &entry = registry->bodies[(size_t)idx];
        out_info->id = entry.id;
        out_info->system_id = entry.system_id;
        out_info->kind = entry.kind;
        out_info->radius_m = entry.radius_m;
        out_info->mu_m3_s2 = entry.mu_m3_s2;
        out_info->rotation_period_ticks = entry.rotation_period_ticks;
        out_info->rotation_epoch_tick = entry.rotation_epoch_tick;
        out_info->axial_tilt_turns = entry.axial_tilt_turns;
        out_info->has_axial_tilt = entry.has_axial_tilt;
        out_info->string_id = entry.string_id.empty() ? 0 : entry.string_id.c_str();
        out_info->string_id_len = (u32)entry.string_id.size();
    }
    return DOM_BODY_REGISTRY_OK;
}

int dom_body_registry_iterate(const dom_body_registry *registry,
                              dom_body_iter_fn fn,
                              void *user) {
    size_t i;
    if (!registry || !fn) {
        return DOM_BODY_REGISTRY_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->bodies.size(); ++i) {
        const BodyEntry &entry = registry->bodies[i];
        dom_body_info info;
        info.id = entry.id;
        info.system_id = entry.system_id;
        info.kind = entry.kind;
        info.radius_m = entry.radius_m;
        info.mu_m3_s2 = entry.mu_m3_s2;
        info.rotation_period_ticks = entry.rotation_period_ticks;
        info.rotation_epoch_tick = entry.rotation_epoch_tick;
        info.axial_tilt_turns = entry.axial_tilt_turns;
        info.has_axial_tilt = entry.has_axial_tilt;
        info.string_id = entry.string_id.empty() ? 0 : entry.string_id.c_str();
        info.string_id_len = (u32)entry.string_id.size();
        fn(&info, user);
    }
    return DOM_BODY_REGISTRY_OK;
}

u32 dom_body_registry_count(const dom_body_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->bodies.size();
}

int dom_body_registry_add_baseline(dom_body_registry *registry) {
    dom_body_desc desc;
    dom_system_id sol_id = 0ull;
    dom_body_id earth_id = 0ull;
    int rc;

    if (!registry) {
        return DOM_BODY_REGISTRY_INVALID_ARGUMENT;
    }
    rc = compute_hash_id("sol", 3u, &sol_id);
    if (rc != DOM_BODY_REGISTRY_OK) {
        return rc;
    }
    rc = compute_hash_id("earth", 5u, &earth_id);
    if (rc != DOM_BODY_REGISTRY_OK) {
        return rc;
    }

    desc.string_id = "earth";
    desc.string_id_len = 5u;
    desc.id = earth_id;
    desc.system_id = sol_id;
    desc.kind = DOM_BODY_KIND_PLANET;
    desc.radius_m = d_q48_16_from_int(6371000);
    desc.mu_m3_s2 = 398600441800000ull;
    desc.rotation_period_ticks = 5169840ull;
    desc.rotation_epoch_tick = 0ull;
    desc.axial_tilt_turns = 0;
    desc.has_axial_tilt = 0u;

    rc = dom_body_registry_register(registry, &desc);
    if (rc == DOM_BODY_REGISTRY_DUPLICATE_ID) {
        return DOM_BODY_REGISTRY_OK;
    }
    return rc;
}
