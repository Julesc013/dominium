/*
FILE: source/dominium/tools/coredata_compile/coredata_validate.cpp
MODULE: Dominium
PURPOSE: Coredata compiler validation (bounds + references).
*/
#include "coredata_validate.h"

#include <algorithm>
#include <cctype>
#include <map>
#include <set>

#include "coredata_schema.h"

namespace dom {
namespace tools {

namespace {

static void add_error(std::vector<CoredataError> &errors,
                      const char *code,
                      const std::string &message) {
    CoredataError e;
    e.path = "validation";
    e.line = 0;
    e.code = code ? code : "error";
    e.message = message;
    errors.push_back(e);
}

static bool is_canonical_id(const std::string &id) {
    size_t i;
    if (id.empty()) {
        return false;
    }
    if (id[0] < 'a' || id[0] > 'z') {
        return false;
    }
    for (i = 0u; i < id.size(); ++i) {
        char c = id[i];
        if ((c >= 'a' && c <= 'z') ||
            (c >= '0' && c <= '9') ||
            c == '_') {
            continue;
        }
        return false;
    }
    return true;
}

static bool q16_in_range(i32 v, i32 min_q16, i32 max_q16) {
    return v >= min_q16 && v <= max_q16;
}

static bool region_type_known(const std::string &s) {
    return (s == "nebula" ||
            s == "open_cluster" ||
            s == "globular_cluster" ||
            s == "galactic_core");
}

static bool system_class_known(const std::string &s) {
    return (s == "single" ||
            s == "binary" ||
            s == "cluster" ||
            s == "remnant" ||
            s == "exotic");
}

static bool evidence_grade_known(const std::string &s) {
    return (s == "confirmed" ||
            s == "candidate" ||
            s == "historical" ||
            s == "fictionalized");
}

} // namespace

bool coredata_validate(const CoredataData &data,
                       std::vector<CoredataError> &errors) {
    std::set<std::string> anchor_ids;
    std::set<std::string> system_profile_ids;
    std::set<std::string> site_profile_ids;
    std::set<std::string> astro_ids;
    size_t i;

    const i32 kQ16Min = 0;
    const i32 kQ16Max = 10 * 65536;
    const u32 kAnchorWeightMin = 1u;
    const u32 kAnchorWeightMax = 100u;

    for (i = 0u; i < data.system_profiles.size(); ++i) {
        const CoredataSystemProfile &p = data.system_profiles[i];
        if (!is_canonical_id(p.id)) {
            add_error(errors, "system_profile_id_invalid", p.id);
        }
        if (!system_profile_ids.insert(p.id).second) {
            add_error(errors, "system_profile_id_duplicate", p.id);
        }
        if (!q16_in_range(p.navigation_instability_q16, kQ16Min, kQ16Max) ||
            !q16_in_range(p.debris_collision_q16, kQ16Min, kQ16Max) ||
            !q16_in_range(p.radiation_baseline_q16, kQ16Min, kQ16Max) ||
            !q16_in_range(p.warp_cap_q16, kQ16Min, kQ16Max) ||
            !q16_in_range(p.survey_difficulty_q16, kQ16Min, kQ16Max)) {
            add_error(errors, "system_profile_bounds", p.id);
        }
        if (p.has_supernova_ticks && p.supernova_timer_ticks == 0ull) {
            add_error(errors, "system_profile_supernova_zero", p.id);
        }
    }

    for (i = 0u; i < data.site_profiles.size(); ++i) {
        const CoredataSiteProfile &p = data.site_profiles[i];
        std::set<std::string> res_ids;
        size_t j;
        if (!is_canonical_id(p.id)) {
            add_error(errors, "site_profile_id_invalid", p.id);
        }
        if (!site_profile_ids.insert(p.id).second) {
            add_error(errors, "site_profile_id_duplicate", p.id);
        }
        if (!q16_in_range(p.hazard_radiation_q16, kQ16Min, kQ16Max) ||
            !q16_in_range(p.hazard_pressure_q16, kQ16Min, kQ16Max) ||
            !q16_in_range(p.corrosion_rate_q16, kQ16Min, kQ16Max) ||
            !q16_in_range(p.temperature_extreme_q16, kQ16Min, kQ16Max)) {
            add_error(errors, "site_profile_bounds", p.id);
        }
        for (j = 0u; j < p.resource_yield.size(); ++j) {
            const CoredataResourceModifier &m = p.resource_yield[j];
            if (!is_canonical_id(m.resource_id)) {
                add_error(errors, "resource_id_invalid", m.resource_id);
            }
            if (!res_ids.insert(m.resource_id).second) {
                add_error(errors, "resource_id_duplicate", m.resource_id);
            }
            if (!q16_in_range(m.modifier_q16, kQ16Min, kQ16Max)) {
                add_error(errors, "resource_modifier_bounds", p.id);
            }
        }
        for (j = 0u; j < p.access_constraints.size(); ++j) {
            if (p.access_constraints[j].empty()) {
                add_error(errors, "access_constraint_empty", p.id);
            }
        }
    }

    for (i = 0u; i < data.anchors.size(); ++i) {
        const CoredataAnchor &a = data.anchors[i];
        if (!is_canonical_id(a.id)) {
            add_error(errors, "anchor_id_invalid", a.id);
        }
        if (!anchor_ids.insert(a.id).second) {
            add_error(errors, "anchor_id_duplicate", a.id);
        }
        if (a.kind != "system" && a.kind != "region") {
            add_error(errors, "anchor_kind_invalid", a.id);
        }
        if (a.kind == "system") {
            if (a.system_class.empty() || !system_class_known(a.system_class)) {
                add_error(errors, "system_class_invalid", a.id);
            }
            if (!a.region_type.empty()) {
                add_error(errors, "region_type_not_allowed", a.id);
            }
        } else if (a.kind == "region") {
            if (a.region_type.empty() || !region_type_known(a.region_type)) {
                add_error(errors, "region_type_invalid", a.id);
            }
            if (!a.system_class.empty()) {
                add_error(errors, "system_class_not_allowed", a.id);
            }
        }
        if (!evidence_grade_known(a.evidence_grade)) {
            add_error(errors, "evidence_grade_invalid", a.id);
        }
        if (a.mechanics_profile_id.empty() ||
            system_profile_ids.find(a.mechanics_profile_id) == system_profile_ids.end()) {
            add_error(errors, "mechanics_profile_missing", a.id);
        }
        if (a.anchor_weight < kAnchorWeightMin || a.anchor_weight > kAnchorWeightMax) {
            add_error(errors, "anchor_weight_out_of_range", a.id);
        }
        if (!a.tags.empty()) {
            size_t t;
            for (t = 0u; t < a.tags.size(); ++t) {
                if (a.tags[t].empty()) {
                    add_error(errors, "anchor_tag_empty", a.id);
                }
            }
        }
    }

    if (data.rules.empty()) {
        add_error(errors, "procedural_rules_missing", "procedural_rules.toml");
    } else {
        const CoredataProceduralRules &r = data.rules[0];
        const i32 kRatioMin = 0;
        const i32 kRatioMax = 65536;
        std::set<std::string> region_keys;
        size_t j;
        if (r.systems_per_anchor_min == 0u ||
            r.systems_per_anchor_max == 0u ||
            r.systems_per_anchor_min > r.systems_per_anchor_max) {
            add_error(errors, "procedural_systems_per_anchor_range", "invalid range");
        }
        if (!q16_in_range(r.red_dwarf_ratio_q16, kRatioMin, kRatioMax) ||
            !q16_in_range(r.binary_ratio_q16, kRatioMin, kRatioMax) ||
            !q16_in_range(r.exotic_ratio_q16, kRatioMin, kRatioMax)) {
            add_error(errors, "procedural_ratio_bounds", "ratio out of range");
        }
        region_keys.clear();
        for (j = 0u; j < r.cluster_density.size(); ++j) {
            if (!region_type_known(r.cluster_density[j].region_type)) {
                add_error(errors, "procedural_region_type_invalid", r.cluster_density[j].region_type);
            }
            region_keys.insert(r.cluster_density[j].region_type);
        }
        if (region_keys.size() != 4u) {
            add_error(errors, "procedural_cluster_density_missing", "region coverage");
        }
        region_keys.clear();
        for (j = 0u; j < r.metallicity_bias.size(); ++j) {
            if (!region_type_known(r.metallicity_bias[j].region_type)) {
                add_error(errors, "procedural_region_type_invalid", r.metallicity_bias[j].region_type);
            }
            region_keys.insert(r.metallicity_bias[j].region_type);
        }
        if (region_keys.size() != 4u) {
            add_error(errors, "procedural_metallicity_missing", "region coverage");
        }
        region_keys.clear();
        for (j = 0u; j < r.hazard_frequency.size(); ++j) {
            if (!region_type_known(r.hazard_frequency[j].region_type)) {
                add_error(errors, "procedural_region_type_invalid", r.hazard_frequency[j].region_type);
            }
            region_keys.insert(r.hazard_frequency[j].region_type);
        }
        if (region_keys.size() != 4u) {
            add_error(errors, "procedural_hazard_missing", "region coverage");
        }
    }

    for (i = 0u; i < data.astro_bodies.size(); ++i) {
        const CoredataAstroBody &b = data.astro_bodies[i];
        if (!is_canonical_id(b.id)) {
            add_error(errors, "astro_id_invalid", b.id);
        }
        if (!astro_ids.insert(b.id).second) {
            add_error(errors, "astro_id_duplicate", b.id);
        }
        if (b.mu_mantissa == 0ull) {
            add_error(errors, "astro_mu_missing", b.id);
        }
        if (b.has_radius && b.radius_m == 0ull) {
            add_error(errors, "astro_radius_invalid", b.id);
        }
        if (b.has_rotation_rate && b.rotation_rate_q16 <= 0) {
            add_error(errors, "astro_rotation_invalid", b.id);
        }
        if (!b.atmosphere_profile_id.empty() && !is_canonical_id(b.atmosphere_profile_id)) {
            add_error(errors, "astro_atmos_profile_invalid", b.id);
        }
    }

    return errors.empty();
}

} // namespace tools
} // namespace dom
