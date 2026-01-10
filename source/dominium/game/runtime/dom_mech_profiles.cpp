/*
FILE: source/dominium/game/runtime/dom_mech_profiles.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/mech_profiles
RESPONSIBILITY: Deterministic mechanics profile registry (system + site).
*/
#include "runtime/dom_mech_profiles.h"

#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct SystemEntry {
    dom_mech_profile_id id_hash;
    std::string id;
    i32 navigation_instability_q16;
    i32 debris_collision_q16;
    i32 radiation_baseline_q16;
    i32 warp_cap_modifier_q16;
    i32 survey_difficulty_q16;
    u64 supernova_timer_ticks;
    u8 has_supernova_timer;
};

struct SiteEntry {
    dom_mech_profile_id id_hash;
    std::string id;
    i32 hazard_radiation_q16;
    i32 hazard_pressure_q16;
    i32 corrosion_rate_q16;
    i32 temperature_extreme_q16;
};

static int compute_hash_id(const char *bytes, u32 len, dom_mech_profile_id *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_MECH_PROFILES_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_MECH_PROFILES_INVALID_DATA;
    }
    if (hash == 0ull) {
        return DOM_MECH_PROFILES_INVALID_DATA;
    }
    *out_id = hash;
    return DOM_MECH_PROFILES_OK;
}

static int find_system_index(const std::vector<SystemEntry> &list, dom_mech_profile_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id_hash == id_hash) {
            return (int)i;
        }
    }
    return -1;
}

static int find_site_index(const std::vector<SiteEntry> &list, dom_mech_profile_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id_hash == id_hash) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_sorted_system(std::vector<SystemEntry> &list, const SystemEntry &entry) {
    size_t i = 0u;
    while (i < list.size()) {
        if (entry.id_hash < list[i].id_hash) {
            break;
        }
        if (entry.id_hash == list[i].id_hash && entry.id < list[i].id) {
            break;
        }
        ++i;
    }
    list.insert(list.begin() + (std::vector<SystemEntry>::difference_type)i, entry);
}

static void insert_sorted_site(std::vector<SiteEntry> &list, const SiteEntry &entry) {
    size_t i = 0u;
    while (i < list.size()) {
        if (entry.id_hash < list[i].id_hash) {
            break;
        }
        if (entry.id_hash == list[i].id_hash && entry.id < list[i].id) {
            break;
        }
        ++i;
    }
    list.insert(list.begin() + (std::vector<SiteEntry>::difference_type)i, entry);
}

} // namespace

struct dom_mech_profiles {
    std::vector<SystemEntry> systems;
    std::vector<SiteEntry> sites;
};

dom_mech_profiles *dom_mech_profiles_create(void) {
    return new dom_mech_profiles();
}

void dom_mech_profiles_destroy(dom_mech_profiles *profiles) {
    if (!profiles) {
        return;
    }
    delete profiles;
}

int dom_mech_profiles_register_system(dom_mech_profiles *profiles,
                                      const dom_mech_system_profile_desc *desc) {
    dom_mech_profile_id id_hash = 0ull;
    SystemEntry entry;
    int rc;
    if (!profiles || !desc) {
        return DOM_MECH_PROFILES_INVALID_ARGUMENT;
    }
    if (!desc->id || desc->id_len == 0u) {
        return DOM_MECH_PROFILES_INVALID_DATA;
    }
    rc = compute_hash_id(desc->id, desc->id_len, &id_hash);
    if (rc != DOM_MECH_PROFILES_OK) {
        return rc;
    }
    if (desc->id_hash != 0ull && desc->id_hash != id_hash) {
        return DOM_MECH_PROFILES_INVALID_DATA;
    }
    if (find_system_index(profiles->systems, id_hash) >= 0) {
        return DOM_MECH_PROFILES_DUPLICATE_ID;
    }
    entry.id_hash = id_hash;
    entry.id.assign(desc->id, desc->id_len);
    entry.navigation_instability_q16 = desc->navigation_instability_q16;
    entry.debris_collision_q16 = desc->debris_collision_q16;
    entry.radiation_baseline_q16 = desc->radiation_baseline_q16;
    entry.warp_cap_modifier_q16 = desc->warp_cap_modifier_q16;
    entry.survey_difficulty_q16 = desc->survey_difficulty_q16;
    entry.supernova_timer_ticks = desc->supernova_timer_ticks;
    entry.has_supernova_timer = desc->has_supernova_timer;
    insert_sorted_system(profiles->systems, entry);
    return DOM_MECH_PROFILES_OK;
}

int dom_mech_profiles_register_site(dom_mech_profiles *profiles,
                                    const dom_mech_site_profile_desc *desc) {
    dom_mech_profile_id id_hash = 0ull;
    SiteEntry entry;
    int rc;
    if (!profiles || !desc) {
        return DOM_MECH_PROFILES_INVALID_ARGUMENT;
    }
    if (!desc->id || desc->id_len == 0u) {
        return DOM_MECH_PROFILES_INVALID_DATA;
    }
    rc = compute_hash_id(desc->id, desc->id_len, &id_hash);
    if (rc != DOM_MECH_PROFILES_OK) {
        return rc;
    }
    if (desc->id_hash != 0ull && desc->id_hash != id_hash) {
        return DOM_MECH_PROFILES_INVALID_DATA;
    }
    if (find_site_index(profiles->sites, id_hash) >= 0) {
        return DOM_MECH_PROFILES_DUPLICATE_ID;
    }
    entry.id_hash = id_hash;
    entry.id.assign(desc->id, desc->id_len);
    entry.hazard_radiation_q16 = desc->hazard_radiation_q16;
    entry.hazard_pressure_q16 = desc->hazard_pressure_q16;
    entry.corrosion_rate_q16 = desc->corrosion_rate_q16;
    entry.temperature_extreme_q16 = desc->temperature_extreme_q16;
    insert_sorted_site(profiles->sites, entry);
    return DOM_MECH_PROFILES_OK;
}

int dom_mech_profiles_get_system(const dom_mech_profiles *profiles,
                                 dom_mech_profile_id id_hash,
                                 dom_mech_system_profile_info *out_info) {
    int idx;
    if (!profiles || !out_info) {
        return DOM_MECH_PROFILES_INVALID_ARGUMENT;
    }
    idx = find_system_index(profiles->systems, id_hash);
    if (idx < 0) {
        return DOM_MECH_PROFILES_NOT_FOUND;
    }
    {
        const SystemEntry &entry = profiles->systems[(size_t)idx];
        out_info->id_hash = entry.id_hash;
        out_info->id = entry.id.empty() ? 0 : entry.id.c_str();
        out_info->id_len = (u32)entry.id.size();
        out_info->navigation_instability_q16 = entry.navigation_instability_q16;
        out_info->debris_collision_q16 = entry.debris_collision_q16;
        out_info->radiation_baseline_q16 = entry.radiation_baseline_q16;
        out_info->warp_cap_modifier_q16 = entry.warp_cap_modifier_q16;
        out_info->survey_difficulty_q16 = entry.survey_difficulty_q16;
        out_info->supernova_timer_ticks = entry.supernova_timer_ticks;
        out_info->has_supernova_timer = entry.has_supernova_timer;
    }
    return DOM_MECH_PROFILES_OK;
}

int dom_mech_profiles_get_site(const dom_mech_profiles *profiles,
                               dom_mech_profile_id id_hash,
                               dom_mech_site_profile_info *out_info) {
    int idx;
    if (!profiles || !out_info) {
        return DOM_MECH_PROFILES_INVALID_ARGUMENT;
    }
    idx = find_site_index(profiles->sites, id_hash);
    if (idx < 0) {
        return DOM_MECH_PROFILES_NOT_FOUND;
    }
    {
        const SiteEntry &entry = profiles->sites[(size_t)idx];
        out_info->id_hash = entry.id_hash;
        out_info->id = entry.id.empty() ? 0 : entry.id.c_str();
        out_info->id_len = (u32)entry.id.size();
        out_info->hazard_radiation_q16 = entry.hazard_radiation_q16;
        out_info->hazard_pressure_q16 = entry.hazard_pressure_q16;
        out_info->corrosion_rate_q16 = entry.corrosion_rate_q16;
        out_info->temperature_extreme_q16 = entry.temperature_extreme_q16;
    }
    return DOM_MECH_PROFILES_OK;
}

int dom_mech_profiles_iterate_system(const dom_mech_profiles *profiles,
                                     dom_mech_system_iter_fn fn,
                                     void *user) {
    size_t i;
    if (!profiles || !fn) {
        return DOM_MECH_PROFILES_INVALID_ARGUMENT;
    }
    for (i = 0u; i < profiles->systems.size(); ++i) {
        const SystemEntry &entry = profiles->systems[i];
        dom_mech_system_profile_info info;
        info.id_hash = entry.id_hash;
        info.id = entry.id.empty() ? 0 : entry.id.c_str();
        info.id_len = (u32)entry.id.size();
        info.navigation_instability_q16 = entry.navigation_instability_q16;
        info.debris_collision_q16 = entry.debris_collision_q16;
        info.radiation_baseline_q16 = entry.radiation_baseline_q16;
        info.warp_cap_modifier_q16 = entry.warp_cap_modifier_q16;
        info.survey_difficulty_q16 = entry.survey_difficulty_q16;
        info.supernova_timer_ticks = entry.supernova_timer_ticks;
        info.has_supernova_timer = entry.has_supernova_timer;
        fn(&info, user);
    }
    return DOM_MECH_PROFILES_OK;
}

int dom_mech_profiles_iterate_site(const dom_mech_profiles *profiles,
                                   dom_mech_site_iter_fn fn,
                                   void *user) {
    size_t i;
    if (!profiles || !fn) {
        return DOM_MECH_PROFILES_INVALID_ARGUMENT;
    }
    for (i = 0u; i < profiles->sites.size(); ++i) {
        const SiteEntry &entry = profiles->sites[i];
        dom_mech_site_profile_info info;
        info.id_hash = entry.id_hash;
        info.id = entry.id.empty() ? 0 : entry.id.c_str();
        info.id_len = (u32)entry.id.size();
        info.hazard_radiation_q16 = entry.hazard_radiation_q16;
        info.hazard_pressure_q16 = entry.hazard_pressure_q16;
        info.corrosion_rate_q16 = entry.corrosion_rate_q16;
        info.temperature_extreme_q16 = entry.temperature_extreme_q16;
        fn(&info, user);
    }
    return DOM_MECH_PROFILES_OK;
}

u32 dom_mech_profiles_system_count(const dom_mech_profiles *profiles) {
    if (!profiles) {
        return 0u;
    }
    return (u32)profiles->systems.size();
}

u32 dom_mech_profiles_site_count(const dom_mech_profiles *profiles) {
    if (!profiles) {
        return 0u;
    }
    return (u32)profiles->sites.size();
}
