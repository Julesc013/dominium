/*
FILE: source/dominium/tools/coredata_compile/coredata_load.h
MODULE: Dominium
PURPOSE: Coredata compiler loader (TOML authoring -> in-memory structs).
*/
#ifndef DOMINIUM_TOOLS_COREDATA_LOAD_H
#define DOMINIUM_TOOLS_COREDATA_LOAD_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace tools {

struct CoredataError {
    std::string path;
    int line;
    std::string code;
    std::string message;
};

struct CoredataAnchor {
    std::string id;
    std::string kind;
    std::string display_name;
    std::string system_class;
    std::string region_type;
    std::string evidence_grade;
    std::string mechanics_profile_id;
    u32 anchor_weight;
    std::vector<std::string> tags;
    bool has_present_pos;
    i32 present_pos_q16[3];

    CoredataAnchor();
};

struct CoredataRulesEntry {
    std::string region_type;
    i32 value_q16;
};

struct CoredataProceduralRules {
    bool present;
    u32 systems_per_anchor_min;
    u32 systems_per_anchor_max;
    i32 red_dwarf_ratio_q16;
    i32 binary_ratio_q16;
    i32 exotic_ratio_q16;
    std::vector<CoredataRulesEntry> cluster_density;
    std::vector<CoredataRulesEntry> metallicity_bias;
    std::vector<CoredataRulesEntry> hazard_frequency;

    CoredataProceduralRules();
};

struct CoredataSystemProfile {
    std::string id;
    i32 navigation_instability_q16;
    i32 debris_collision_q16;
    i32 radiation_baseline_q16;
    i32 warp_cap_q16;
    i32 survey_difficulty_q16;
    bool has_supernova_ticks;
    u64 supernova_timer_ticks;

    CoredataSystemProfile();
};

struct CoredataResourceModifier {
    std::string resource_id;
    i32 modifier_q16;
};

struct CoredataSiteProfile {
    std::string id;
    i32 hazard_radiation_q16;
    i32 hazard_pressure_q16;
    i32 corrosion_rate_q16;
    i32 temperature_extreme_q16;
    std::vector<CoredataResourceModifier> resource_yield;
    std::vector<std::string> access_constraints;

    CoredataSiteProfile();
};

struct CoredataAstroBody {
    std::string id;
    bool has_radius;
    u64 radius_m;
    u64 mu_mantissa;
    i32 mu_exp10;
    bool has_rotation_rate;
    i32 rotation_rate_q16;
    std::string atmosphere_profile_id;

    CoredataAstroBody();
};

struct CoredataData {
    std::vector<CoredataAnchor> anchors;
    std::vector<CoredataProceduralRules> rules; /* size 0 or 1 */
    std::vector<CoredataSystemProfile> system_profiles;
    std::vector<CoredataSiteProfile> site_profiles;
    std::vector<CoredataAstroBody> astro_bodies;
};

bool coredata_load_all(const std::string &root,
                       CoredataData &out,
                       std::vector<CoredataError> &errors);

void coredata_errors_print(const std::vector<CoredataError> &errors);

} // namespace tools
} // namespace dom

#endif /* DOMINIUM_TOOLS_COREDATA_LOAD_H */
