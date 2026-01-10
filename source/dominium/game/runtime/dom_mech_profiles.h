/*
FILE: source/dominium/game/runtime/dom_mech_profiles.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/mech_profiles
RESPONSIBILITY: Deterministic mechanics profile registry (system + site).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_MECH_PROFILES_H
#define DOM_MECH_PROFILES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_MECH_PROFILES_OK = 0,
    DOM_MECH_PROFILES_ERR = -1,
    DOM_MECH_PROFILES_INVALID_ARGUMENT = -2,
    DOM_MECH_PROFILES_DUPLICATE_ID = -3,
    DOM_MECH_PROFILES_INVALID_DATA = -4,
    DOM_MECH_PROFILES_NOT_FOUND = -5
};

typedef u64 dom_mech_profile_id;

typedef struct dom_mech_system_profile_desc {
    const char *id;
    u32 id_len;
    dom_mech_profile_id id_hash;
    i32 navigation_instability_q16;
    i32 debris_collision_q16;
    i32 radiation_baseline_q16;
    i32 warp_cap_modifier_q16;
    i32 survey_difficulty_q16;
    u64 supernova_timer_ticks;
    u8 has_supernova_timer;
} dom_mech_system_profile_desc;

typedef struct dom_mech_system_profile_info {
    dom_mech_profile_id id_hash;
    const char *id;
    u32 id_len;
    i32 navigation_instability_q16;
    i32 debris_collision_q16;
    i32 radiation_baseline_q16;
    i32 warp_cap_modifier_q16;
    i32 survey_difficulty_q16;
    u64 supernova_timer_ticks;
    u8 has_supernova_timer;
} dom_mech_system_profile_info;

typedef struct dom_mech_site_profile_desc {
    const char *id;
    u32 id_len;
    dom_mech_profile_id id_hash;
    i32 hazard_radiation_q16;
    i32 hazard_pressure_q16;
    i32 corrosion_rate_q16;
    i32 temperature_extreme_q16;
} dom_mech_site_profile_desc;

typedef struct dom_mech_site_profile_info {
    dom_mech_profile_id id_hash;
    const char *id;
    u32 id_len;
    i32 hazard_radiation_q16;
    i32 hazard_pressure_q16;
    i32 corrosion_rate_q16;
    i32 temperature_extreme_q16;
} dom_mech_site_profile_info;

typedef void (*dom_mech_system_iter_fn)(const dom_mech_system_profile_info *info, void *user);
typedef void (*dom_mech_site_iter_fn)(const dom_mech_site_profile_info *info, void *user);

typedef struct dom_mech_profiles dom_mech_profiles;

dom_mech_profiles *dom_mech_profiles_create(void);
void dom_mech_profiles_destroy(dom_mech_profiles *profiles);

int dom_mech_profiles_register_system(dom_mech_profiles *profiles,
                                      const dom_mech_system_profile_desc *desc);
int dom_mech_profiles_register_site(dom_mech_profiles *profiles,
                                    const dom_mech_site_profile_desc *desc);

int dom_mech_profiles_get_system(const dom_mech_profiles *profiles,
                                 dom_mech_profile_id id_hash,
                                 dom_mech_system_profile_info *out_info);
int dom_mech_profiles_get_site(const dom_mech_profiles *profiles,
                               dom_mech_profile_id id_hash,
                               dom_mech_site_profile_info *out_info);

int dom_mech_profiles_iterate_system(const dom_mech_profiles *profiles,
                                     dom_mech_system_iter_fn fn,
                                     void *user);
int dom_mech_profiles_iterate_site(const dom_mech_profiles *profiles,
                                   dom_mech_site_iter_fn fn,
                                   void *user);

u32 dom_mech_profiles_system_count(const dom_mech_profiles *profiles);
u32 dom_mech_profiles_site_count(const dom_mech_profiles *profiles);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_MECH_PROFILES_H */
