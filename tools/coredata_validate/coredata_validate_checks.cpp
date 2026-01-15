/*
FILE: source/dominium/tools/coredata_validate/coredata_validate_checks.cpp
MODULE: Dominium
PURPOSE: Coredata validator checks for authoring data and compiled packs.
*/
#include "coredata_validate_checks.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <map>
#include <set>

#include "coredata_compile/coredata_manifest.h"
#include "coredata_compile/coredata_schema.h"
#include "dominium/core_tlv.h"

extern "C" {
#include "domino/core/spacetime.h"
}

namespace dom {
namespace tools {

namespace {

static CoredataValidationClass classify_error_code(const std::string &code) {
    if (code == "mechanics_profile_missing" ||
        code.find("missing_profile") != std::string::npos) {
        return CORE_DATA_REFERENCE_ERROR;
    }
    if (code == "system_profile_supernova_zero" ||
        code == "astro_radius_invalid" ||
        code == "astro_rotation_invalid" ||
        code.find("bounds") != std::string::npos ||
        code.find("out_of_range") != std::string::npos ||
        code.find("_range") != std::string::npos) {
        return CORE_DATA_RANGE_ERROR;
    }
    return CORE_DATA_SCHEMA_ERROR;
}

static void add_policy(CoredataValidationReport &report,
                       const std::string &code,
                       const std::string &message,
                       const std::string &path) {
    coredata_report_add_issue(report,
                              CORE_DATA_POLICY_ERROR,
                              CORE_DATA_SEVERITY_ERROR,
                              code,
                              message,
                              path,
                              0);
}

static void add_determinism(CoredataValidationReport &report,
                            const std::string &code,
                            const std::string &message,
                            const std::string &path) {
    coredata_report_add_issue(report,
                              CORE_DATA_DETERMINISM_ERROR,
                              CORE_DATA_SEVERITY_ERROR,
                              code,
                              message,
                              path,
                              0);
}

static void add_schema(CoredataValidationReport &report,
                       const std::string &code,
                       const std::string &message,
                       const std::string &path) {
    coredata_report_add_issue(report,
                              CORE_DATA_SCHEMA_ERROR,
                              CORE_DATA_SEVERITY_ERROR,
                              code,
                              message,
                              path,
                              0);
}

static void add_migration(CoredataValidationReport &report,
                          const std::string &code,
                          const std::string &message,
                          const std::string &path) {
    coredata_report_add_issue(report,
                              CORE_DATA_MIGRATION_ERROR,
                              CORE_DATA_SEVERITY_ERROR,
                              code,
                              message,
                              path,
                              0);
}

static bool record_less(const CoredataPackRecordView &a,
                        const CoredataPackRecordView &b) {
    if (a.type_id != b.type_id) {
        return a.type_id < b.type_id;
    }
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static u64 hash_content(const std::vector<CoredataPackRecordView> &records) {
    std::vector<unsigned char> buf;
    size_t i;
    buf.reserve(records.size() * 8u);
    for (i = 0u; i < records.size(); ++i) {
        unsigned char tmp[8];
        dom::core_tlv::tlv_write_u64_le(tmp, records[i].record_hash);
        buf.insert(buf.end(), tmp, tmp + 8u);
    }
    return dom::core_tlv::tlv_fnv1a64(buf.empty() ? 0 : &buf[0], buf.size());
}

static bool has_tag(const std::vector<std::string> &tags, const char *tag) {
    size_t i;
    for (i = 0u; i < tags.size(); ++i) {
        if (tags[i] == tag) {
            return true;
        }
    }
    return false;
}

static bool starts_with(const std::string &s, const char *prefix) {
    size_t len = std::strlen(prefix);
    if (s.size() < len) {
        return false;
    }
    return s.compare(0u, len, prefix) == 0;
}

} // namespace

void coredata_validate_report_errors(const std::vector<CoredataError> &errors,
                                     CoredataValidationReport &report) {
    size_t i;
    for (i = 0u; i < errors.size(); ++i) {
        const CoredataError &err = errors[i];
        CoredataValidationClass cls = classify_error_code(err.code);
        coredata_report_add_issue(report,
                                  cls,
                                  CORE_DATA_SEVERITY_ERROR,
                                  err.code,
                                  err.message,
                                  err.path,
                                  err.line);
    }
}

void coredata_validate_authoring_policy(const CoredataData &data,
                                        CoredataValidationReport &report) {
    size_t i;
    for (i = 0u; i < data.anchors.size(); ++i) {
        const CoredataAnchor &a = data.anchors[i];
        if (a.evidence_grade == "candidate" &&
            (has_tag(a.tags, "progression_critical") || has_tag(a.tags, "critical_path"))) {
            add_policy(report,
                       "policy_candidate_progression",
                       "candidate anchor is progression-critical",
                       a.id);
        }
        if (a.mechanics_profile_id == "galactic_core_extreme") {
            if (!(a.kind == "region" && a.region_type == "galactic_core")) {
                add_policy(report,
                           "policy_galactic_core_binding",
                           "galactic_core_extreme bound to non-core anchor",
                           a.id);
            }
        }
    }

    for (i = 0u; i < data.system_profiles.size(); ++i) {
        const CoredataSystemProfile &p = data.system_profiles[i];
        const i32 kNeutral = 65536;
        bool all_neutral = (p.navigation_instability_q16 == kNeutral &&
                            p.debris_collision_q16 == kNeutral &&
                            p.radiation_baseline_q16 == kNeutral &&
                            p.warp_cap_q16 == kNeutral &&
                            p.survey_difficulty_q16 == kNeutral &&
                            !p.has_supernova_ticks);
        if (all_neutral && !starts_with(p.id, "baseline_")) {
            add_policy(report,
                       "policy_system_profile_neutral",
                       "system profile is fully neutral",
                       p.id);
        }
        if (p.has_supernova_ticks && p.id != "massive_star_short_lived") {
            add_policy(report,
                       "policy_supernova_profile",
                       "supernova_timer_ticks only allowed on massive_star_short_lived",
                       p.id);
        }
    }

    for (i = 0u; i < data.site_profiles.size(); ++i) {
        const CoredataSiteProfile &p = data.site_profiles[i];
        bool all_zero = (p.hazard_radiation_q16 == 0 &&
                         p.hazard_pressure_q16 == 0 &&
                         p.corrosion_rate_q16 == 0 &&
                         p.temperature_extreme_q16 == 0 &&
                         p.resource_yield.empty() &&
                         p.access_constraints.empty());
        if (all_zero) {
            add_policy(report,
                       "policy_site_profile_neutral",
                       "site profile is fully neutral",
                       p.id);
        }
        if (p.hazard_pressure_q16 > 0 && p.access_constraints.empty()) {
            add_policy(report,
                       "policy_pressure_no_constraint",
                       "pressure hazard without access constraints",
                       p.id);
        }
    }
}

void coredata_validate_pack_checks(const CoredataPackView &pack,
                                   const CoredataManifestView *manifest,
                                   CoredataValidationReport &report) {
    std::vector<CoredataPackRecordView> sorted;
    std::map<std::string, u64> manifest_hashes;
    std::set<std::string> seen_ids;
    size_t i;
    size_t anchor_count = 0u;
    size_t rules_count = 0u;
    size_t sys_profile_count = 0u;
    size_t site_profile_count = 0u;
    size_t astro_count = 0u;

    if (!pack.has_pack_meta) {
        add_schema(report, "pack_meta_missing", "pack meta missing", "pack");
    }
    if (pack.pack_schema_version == 0u) {
        add_schema(report, "pack_schema_missing", "pack schema version missing", "pack");
    } else if (pack.pack_schema_version > 1u) {
        add_migration(report, "pack_schema_unsupported", "pack schema version unsupported", "pack");
    }
    if (pack.pack_id.empty()) {
        add_schema(report, "pack_id_missing", "pack id missing", "pack");
    }
    if (pack.pack_version_num == 0u) {
        add_schema(report, "pack_version_missing", "pack version missing", "pack");
    }

    for (i = 0u; i < pack.records.size(); ++i) {
        const CoredataPackRecordView &rec = pack.records[i];
        std::string key;
        u64 hash = 0ull;
        if (rec.type_id == CORE_DATA_REC_COSMO_ANCHOR) {
            anchor_count += 1u;
        } else if (rec.type_id == CORE_DATA_REC_COSMO_RULES) {
            rules_count += 1u;
        } else if (rec.type_id == CORE_DATA_REC_MECH_SYSTEM) {
            sys_profile_count += 1u;
        } else if (rec.type_id == CORE_DATA_REC_MECH_SITE) {
            site_profile_count += 1u;
        } else if (rec.type_id == CORE_DATA_REC_ASTRO_BODY) {
            astro_count += 1u;
        }

        if (!rec.id.empty()) {
            if (dom_id_hash64(rec.id.c_str(), (u32)rec.id.size(), &hash) != DOM_SPACETIME_OK) {
                add_determinism(report, "id_hash_failed", "id hash failed", rec.id);
            } else if (hash != rec.id_hash) {
                add_determinism(report, "id_hash_mismatch", "id hash mismatch", rec.id);
            }
            key = std::string();
            key.reserve(rec.id.size() + 16u);
            {
                char buf[16];
                std::sprintf(buf, "%08u:", rec.type_id);
                key = buf;
                key += rec.id;
            }
            if (!seen_ids.insert(key).second) {
                add_schema(report, "record_duplicate_id", "duplicate record id", rec.id);
            }
        } else {
            if (rec.type_id != CORE_DATA_REC_PACK_META &&
                rec.type_id != CORE_DATA_REC_COSMO_RULES) {
                add_determinism(report, "record_missing_id", "record missing id", "pack");
            }
        }
    }

    if (anchor_count == 0u) {
        add_schema(report, "anchors_missing", "no cosmo anchors present", "pack");
    }
    if (rules_count == 0u) {
        add_schema(report, "rules_missing", "procedural rules missing", "pack");
    } else if (rules_count > 1u) {
        add_determinism(report, "rules_multiple", "multiple procedural rules records", "pack");
    }
    if (sys_profile_count == 0u) {
        add_schema(report, "system_profiles_missing", "system profiles missing", "pack");
    }
    if (site_profile_count == 0u) {
        add_schema(report, "site_profiles_missing", "site profiles missing", "pack");
    }
    if (astro_count == 0u) {
        add_schema(report, "astro_missing", "astro constants missing", "pack");
    }

    for (i = 1u; i < pack.records.size(); ++i) {
        if (record_less(pack.records[i], pack.records[i - 1u])) {
            add_determinism(report, "record_order_invalid", "record order not canonical", "pack");
            break;
        }
    }

    sorted.clear();
    for (i = 0u; i < pack.records.size(); ++i) {
        if (pack.records[i].type_id != CORE_DATA_REC_PACK_META) {
            sorted.push_back(pack.records[i]);
        }
    }
    std::sort(sorted.begin(), sorted.end(), record_less);
    if (pack.content_hash != hash_content(sorted)) {
        add_determinism(report, "content_hash_mismatch", "content hash mismatch", "pack");
    }

    if (!manifest) {
        coredata_report_add_issue(report,
                                  CORE_DATA_SCHEMA_ERROR,
                                  CORE_DATA_SEVERITY_WARNING,
                                  "manifest_missing",
                                  "pack manifest missing",
                                  "pack",
                                  0);
        return;
    }

    if (manifest->schema_version != 1u) {
        add_schema(report, "manifest_schema_invalid", "manifest schema version invalid", "manifest");
    }
    if (manifest->pack_id != pack.pack_id) {
        add_determinism(report, "manifest_pack_id_mismatch", "manifest pack id mismatch", "manifest");
    }
    if (manifest->pack_version_num != pack.pack_version_num) {
        add_determinism(report, "manifest_pack_version_mismatch", "manifest pack version mismatch", "manifest");
    }
    if (manifest->pack_schema_version != pack.pack_schema_version) {
        add_determinism(report, "manifest_pack_schema_mismatch", "manifest pack schema mismatch", "manifest");
    }
    if (manifest->content_hash != pack.content_hash) {
        add_determinism(report, "manifest_content_hash_mismatch", "manifest content hash mismatch", "manifest");
    }
    if (manifest->pack_hash != pack.pack_hash) {
        add_determinism(report, "manifest_pack_hash_mismatch", "manifest pack hash mismatch", "manifest");
    }

    for (i = 0u; i < manifest->records.size(); ++i) {
        const CoredataManifestRecordView &mrec = manifest->records[i];
        std::string key;
        char buf[16];
        std::sprintf(buf, "%08u:", mrec.type_id);
        key = buf;
        key += mrec.id;
        manifest_hashes[key] = mrec.record_hash;
    }
    for (i = 0u; i < pack.records.size(); ++i) {
        const CoredataPackRecordView &rec = pack.records[i];
        std::string key;
        char buf[16];
        std::sprintf(buf, "%08u:", rec.type_id);
        key = buf;
        key += rec.id;
        if (manifest_hashes.find(key) == manifest_hashes.end()) {
            add_determinism(report, "manifest_record_missing", "manifest missing record", rec.id);
        } else if (manifest_hashes[key] != rec.record_hash) {
            add_determinism(report, "manifest_record_hash_mismatch", "manifest record hash mismatch", rec.id);
        }
    }
}

} // namespace tools
} // namespace dom
