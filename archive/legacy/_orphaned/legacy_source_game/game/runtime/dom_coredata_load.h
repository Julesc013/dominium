/*
FILE: source/dominium/game/runtime/dom_coredata_load.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/coredata_load
RESPONSIBILITY: Loads coredata TLV packs and applies them to runtime registries.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_COREDATA_LOAD_H
#define DOM_COREDATA_LOAD_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/fixed.h"
#include "domino/core/types.h"
}

#include "dominium/coredata_schema.h"
#include "runtime/dom_mech_profiles.h"
#include "runtime/dom_system_registry.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_cosmo_graph.h"

enum {
    DOM_COREDATA_OK = 0,
    DOM_COREDATA_ERR = -1,
    DOM_COREDATA_INVALID_ARGUMENT = -2,
    DOM_COREDATA_INVALID_FORMAT = -3,
    DOM_COREDATA_MISSING_REQUIRED = -4,
    DOM_COREDATA_DUPLICATE_ID = -5,
    DOM_COREDATA_MISSING_REFERENCE = -6,
    DOM_COREDATA_IO_ERROR = -7
};

struct dom_coredata_anchor {
    std::string id;
    u64 id_hash;
    u32 kind;
    u32 system_class;
    u32 region_type;
    u32 evidence_grade;
    std::string mechanics_profile_id;
    u64 mechanics_profile_id_hash;
    u32 anchor_weight;
    std::string display_name;
    bool has_present_pos;
    i32 present_pos_q16[3];

    dom_coredata_anchor();
};

struct dom_coredata_edge {
    std::string src_id;
    u64 src_id_hash;
    std::string dst_id;
    u64 dst_id_hash;
    u64 duration_ticks;
    std::string cost_profile_id;
    u64 cost_profile_id_hash;
    std::string hazard_profile_id;
    u64 hazard_profile_id_hash;
    bool has_hazard;

    dom_coredata_edge();
};

struct dom_coredata_rules_entry {
    u32 region_type;
    i32 value_q16;

    dom_coredata_rules_entry();
};

struct dom_coredata_procedural_rules {
    bool present;
    u32 systems_per_anchor_min;
    u32 systems_per_anchor_max;
    i32 red_dwarf_ratio_q16;
    i32 binary_ratio_q16;
    i32 exotic_ratio_q16;
    std::vector<dom_coredata_rules_entry> cluster_density;
    std::vector<dom_coredata_rules_entry> metallicity_bias;
    std::vector<dom_coredata_rules_entry> hazard_frequency;

    dom_coredata_procedural_rules();
};

struct dom_coredata_system_profile {
    std::string id;
    u64 id_hash;
    i32 navigation_instability_q16;
    i32 debris_collision_q16;
    i32 radiation_baseline_q16;
    i32 warp_cap_modifier_q16;
    i32 survey_difficulty_q16;
    u64 supernova_timer_ticks;
    bool has_supernova;

    dom_coredata_system_profile();
};

struct dom_coredata_resource_modifier {
    std::string resource_id;
    u64 resource_id_hash;
    i32 modifier_q16;

    dom_coredata_resource_modifier();
};

struct dom_coredata_site_profile {
    std::string id;
    u64 id_hash;
    i32 hazard_radiation_q16;
    i32 hazard_pressure_q16;
    i32 corrosion_rate_q16;
    i32 temperature_extreme_q16;
    std::vector<dom_coredata_resource_modifier> resource_yield;
    std::vector<std::string> access_constraints;

    dom_coredata_site_profile();
};

struct dom_coredata_astro_body {
    std::string id;
    u64 id_hash;
    bool has_radius;
    u64 radius_m;
    u64 mu_mantissa;
    i32 mu_exp10;
    bool has_rotation_rate;
    i32 rotation_rate_q16;
    std::string atmosphere_profile_id;
    u64 atmosphere_profile_id_hash;

    dom_coredata_astro_body();
};

struct dom_coredata_state {
    u32 pack_schema_version;
    std::string pack_id;
    u32 pack_version_num;
    std::string pack_version_str;
    u64 content_hash;
    u64 pack_hash;
    u64 sim_digest;
    std::vector<dom_coredata_anchor> anchors;
    std::vector<dom_coredata_edge> edges;
    dom_coredata_procedural_rules rules;
    std::vector<dom_coredata_system_profile> system_profiles;
    std::vector<dom_coredata_site_profile> site_profiles;
    std::vector<dom_coredata_astro_body> astro_bodies;

    dom_coredata_state();
};

int dom_coredata_load_from_bytes(const unsigned char *data,
                                 size_t size,
                                 dom_coredata_state *out_state,
                                 std::string *out_error);
int dom_coredata_load_from_file(const char *path,
                                dom_coredata_state *out_state,
                                std::string *out_error);

u64 dom_coredata_compute_sim_digest(const dom_coredata_state *state);

int dom_coredata_apply_to_registries(const dom_coredata_state *state,
                                     dom::dom_cosmo_graph *graph,
                                     dom_mech_profiles *mech_profiles,
                                     dom_system_registry *systems,
                                     dom_body_registry *bodies,
                                     u32 ups,
                                     std::string *out_error);

#endif /* DOM_COREDATA_LOAD_H */
