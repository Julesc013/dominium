/*
FILE: source/dominium/launcher/launcher_coredata_sim.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / coredata_sim
RESPONSIBILITY: Compute coredata sim digest from compiled coredata pack.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: Platform UI headers; non-deterministic inputs.
*/
#include "launcher_coredata_sim.h"

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

#include "dominium/core_tlv.h"
#include "dominium/coredata_schema.h"

namespace dom {

namespace {

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') {
            out[i] = '/';
        }
    }
    return out;
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool read_file_all(const std::string& path, std::vector<unsigned char>& out_bytes) {
    FILE* f;
    long sz;
    size_t got;
    out_bytes.clear();
    f = std::fopen(path.c_str(), "rb");
    if (!f) {
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    if (sz == 0) {
        std::fclose(f);
        return true;
    }
    out_bytes.resize((size_t)sz);
    got = std::fread(out_bytes.empty() ? (void*)0 : &out_bytes[0], 1u, (size_t)sz, f);
    std::fclose(f);
    if (got != (size_t)sz) {
        out_bytes.clear();
        return false;
    }
    return true;
}

static bool parse_u32(const std::string& s, u32& out) {
    char* end = 0;
    unsigned long v = std::strtoul(s.c_str(), &end, 10);
    if (!end || end[0] != '\0') {
        return false;
    }
    out = (u32)v;
    return true;
}

static bool parse_version_num(const std::string& s, u32& out, std::string& err) {
    size_t i = 0u;
    u32 parts[3] = {0u, 0u, 0u};
    int part_index = 0;
    std::string cur;
    if (s.empty()) {
        err = "empty_version";
        return false;
    }
    for (i = 0u; i < s.size(); ++i) {
        char c = s[i];
        if (c == '.') {
            if (part_index >= 2 || cur.empty()) {
                err = "invalid_version";
                return false;
            }
            if (!parse_u32(cur, parts[part_index])) {
                err = "invalid_version";
                return false;
            }
            cur.clear();
            ++part_index;
        } else if (c >= '0' && c <= '9') {
            cur.push_back(c);
        } else {
            err = "invalid_version";
            return false;
        }
    }
    if (!cur.empty()) {
        if (!parse_u32(cur, parts[part_index])) {
            err = "invalid_version";
            return false;
        }
    } else if (part_index > 0) {
        err = "invalid_version";
        return false;
    }

    if (part_index == 0 && s.find('.') == std::string::npos) {
        out = parts[0];
        return true;
    }
    if (parts[0] > 9999u || parts[1] > 99u || parts[2] > 99u) {
        err = "version_out_of_range";
        return false;
    }
    out = (parts[0] * 10000u) + (parts[1] * 100u) + parts[2];
    return true;
}

static std::string format_version_dir(u32 version_num) {
    char buf[16];
    std::sprintf(buf, "%08u", version_num);
    return std::string(buf);
}

static bool str_ieq(const std::string& a, const char* b) {
    size_t i;
    size_t blen;
    if (!b) {
        return false;
    }
    blen = std::strlen(b);
    if (a.size() != blen) {
        return false;
    }
    for (i = 0u; i < blen; ++i) {
        const unsigned char ac = (unsigned char)a[i];
        const unsigned char bc = (unsigned char)b[i];
        if (std::tolower(ac) != std::tolower(bc)) {
            return false;
        }
    }
    return true;
}

static bool is_coredata_pack_id(const std::string& id) {
    return str_ieq(id, "base_cosmo");
}

static bool id_hash64(const std::string& id, u64& out_hash) {
    return dom_id_hash64(id.c_str(), (u32)id.size(), &out_hash) == DOM_SPACETIME_OK;
}

static bool read_u32(const dom::core_tlv::TlvRecord& rec, u32& out) {
    return dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out);
}

static bool read_i32(const dom::core_tlv::TlvRecord& rec, i32& out) {
    return dom::core_tlv::tlv_read_i32_le(rec.payload, rec.len, out);
}

static bool read_u64(const dom::core_tlv::TlvRecord& rec, u64& out) {
    return dom::core_tlv::tlv_read_u64_le(rec.payload, rec.len, out);
}

static std::string read_string(const dom::core_tlv::TlvRecord& rec) {
    return dom::core_tlv::tlv_read_string(rec.payload, rec.len);
}

} // namespace

namespace {

static u64 compute_edge_key_hash(const CoredataEdge& edge) {
    std::string key = edge.src_id + "->" + edge.dst_id;
    u64 hash = 0ull;
    if (dom_id_hash64(key.c_str(), (u32)key.size(), &hash) != DOM_SPACETIME_OK) {
        return 0ull;
    }
    return hash;
}

static bool rules_entry_less(const CoredataRulesEntry& a,
                             const CoredataRulesEntry& b) {
    return a.region_type < b.region_type;
}

static bool resource_mod_less(const CoredataResourceModifier& a,
                              const CoredataResourceModifier& b) {
    return a.resource_id < b.resource_id;
}

static std::vector<CoredataRulesEntry> sorted_rules(const std::vector<CoredataRulesEntry>& in) {
    std::vector<CoredataRulesEntry> out = in;
    std::sort(out.begin(), out.end(), rules_entry_less);
    return out;
}

static std::vector<CoredataResourceModifier> sorted_resources(const std::vector<CoredataResourceModifier>& in) {
    std::vector<CoredataResourceModifier> out = in;
    std::sort(out.begin(), out.end(), resource_mod_less);
    return out;
}

static std::vector<std::string> sorted_strings(const std::vector<std::string>& in) {
    std::vector<std::string> out = in;
    std::sort(out.begin(), out.end());
    return out;
}

static bool build_sim_payload_anchor(const CoredataAnchor& a,
                                     std::vector<unsigned char>& out) {
    dom::core_tlv::TlvWriter w;
    w.add_string(CORE_DATA_ANCHOR_TAG_ID, a.id);
    w.add_u64(CORE_DATA_ANCHOR_TAG_ID_HASH, a.id_hash);
    w.add_u32(CORE_DATA_ANCHOR_TAG_KIND, a.kind);
    if (a.kind == CORE_DATA_KIND_SYSTEM) {
        w.add_u32(CORE_DATA_ANCHOR_TAG_SYSTEM_CLASS, a.system_class);
    } else if (a.kind == CORE_DATA_KIND_REGION) {
        w.add_u32(CORE_DATA_ANCHOR_TAG_REGION_TYPE, a.region_type);
    }
    w.add_u32(CORE_DATA_ANCHOR_TAG_EVIDENCE_GRADE, a.evidence_grade);
    w.add_string(CORE_DATA_ANCHOR_TAG_MECH_PROFILE_ID, a.mechanics_profile_id);
    w.add_u32(CORE_DATA_ANCHOR_TAG_ANCHOR_WEIGHT, a.anchor_weight);
    out = w.bytes();
    return true;
}

static bool build_sim_payload_edge(const CoredataEdge& e,
                                   std::vector<unsigned char>& out) {
    dom::core_tlv::TlvWriter w;
    w.add_string(CORE_DATA_EDGE_TAG_SRC_ID, e.src_id);
    w.add_u64(CORE_DATA_EDGE_TAG_SRC_ID_HASH, e.src_id_hash);
    w.add_string(CORE_DATA_EDGE_TAG_DST_ID, e.dst_id);
    w.add_u64(CORE_DATA_EDGE_TAG_DST_ID_HASH, e.dst_id_hash);
    w.add_u64(CORE_DATA_EDGE_TAG_DURATION_TICKS, e.duration_ticks);
    w.add_string(CORE_DATA_EDGE_TAG_COST_PROFILE_ID, e.cost_profile_id);
    w.add_u64(CORE_DATA_EDGE_TAG_COST_PROFILE_HASH, e.cost_profile_id_hash);
    if (e.has_hazard) {
        w.add_string(CORE_DATA_EDGE_TAG_HAZARD_PROFILE_ID, e.hazard_profile_id);
        w.add_u64(CORE_DATA_EDGE_TAG_HAZARD_PROFILE_HASH, e.hazard_profile_id_hash);
    }
    out = w.bytes();
    return true;
}

static bool build_sim_payload_rules(const CoredataProceduralRules& r,
                                    std::vector<unsigned char>& out) {
    dom::core_tlv::TlvWriter w;
    size_t i;
    w.add_u32(CORE_DATA_RULES_TAG_SYS_MIN, r.systems_per_anchor_min);
    w.add_u32(CORE_DATA_RULES_TAG_SYS_MAX, r.systems_per_anchor_max);
    w.add_i32(CORE_DATA_RULES_TAG_RED_DWARF_RATIO, r.red_dwarf_ratio_q16);
    w.add_i32(CORE_DATA_RULES_TAG_BINARY_RATIO, r.binary_ratio_q16);
    w.add_i32(CORE_DATA_RULES_TAG_EXOTIC_RATIO, r.exotic_ratio_q16);
    {
        std::vector<CoredataRulesEntry> entries = sorted_rules(r.cluster_density);
        for (i = 0u; i < entries.size(); ++i) {
            dom::core_tlv::TlvWriter inner;
            inner.add_u32(CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE, entries[i].region_type);
            inner.add_i32(CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16, entries[i].value_q16);
            w.add_container(CORE_DATA_RULES_TAG_CLUSTER_DENSITY, inner.bytes());
        }
    }
    {
        std::vector<CoredataRulesEntry> entries = sorted_rules(r.metallicity_bias);
        for (i = 0u; i < entries.size(); ++i) {
            dom::core_tlv::TlvWriter inner;
            inner.add_u32(CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE, entries[i].region_type);
            inner.add_i32(CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16, entries[i].value_q16);
            w.add_container(CORE_DATA_RULES_TAG_METALLICITY_BIAS, inner.bytes());
        }
    }
    {
        std::vector<CoredataRulesEntry> entries = sorted_rules(r.hazard_frequency);
        for (i = 0u; i < entries.size(); ++i) {
            dom::core_tlv::TlvWriter inner;
            inner.add_u32(CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE, entries[i].region_type);
            inner.add_i32(CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16, entries[i].value_q16);
            w.add_container(CORE_DATA_RULES_TAG_HAZARD_FREQUENCY, inner.bytes());
        }
    }
    out = w.bytes();
    return true;
}

static bool build_sim_payload_system_profile(const CoredataSystemProfile& p,
                                             std::vector<unsigned char>& out) {
    dom::core_tlv::TlvWriter w;
    w.add_string(CORE_DATA_MECH_SYS_TAG_ID, p.id);
    w.add_u64(CORE_DATA_MECH_SYS_TAG_ID_HASH, p.id_hash);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_NAV_INSTABILITY, p.navigation_instability_q16);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_DEBRIS_COLLISION, p.debris_collision_q16);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_RADIATION_BASELINE, p.radiation_baseline_q16);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_WARP_CAP, p.warp_cap_modifier_q16);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_SURVEY_DIFFICULTY, p.survey_difficulty_q16);
    if (p.has_supernova) {
        w.add_u64(CORE_DATA_MECH_SYS_TAG_SUPERNOVA_TICKS, p.supernova_timer_ticks);
    }
    out = w.bytes();
    return true;
}

static bool build_sim_payload_site_profile(const CoredataSiteProfile& p,
                                           std::vector<unsigned char>& out) {
    dom::core_tlv::TlvWriter w;
    size_t i;
    w.add_string(CORE_DATA_MECH_SITE_TAG_ID, p.id);
    w.add_u64(CORE_DATA_MECH_SITE_TAG_ID_HASH, p.id_hash);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_HAZARD_RAD, p.hazard_radiation_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_HAZARD_PRESS, p.hazard_pressure_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_CORROSION_RATE, p.corrosion_rate_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_TEMP_EXTREME, p.temperature_extreme_q16);
    {
        std::vector<CoredataResourceModifier> mods = sorted_resources(p.resource_yield);
        for (i = 0u; i < mods.size(); ++i) {
            dom::core_tlv::TlvWriter inner;
            inner.add_string(CORE_DATA_MECH_SITE_RES_TAG_ID, mods[i].resource_id);
            inner.add_i32(CORE_DATA_MECH_SITE_RES_TAG_MOD_Q16, mods[i].modifier_q16);
            w.add_container(CORE_DATA_MECH_SITE_TAG_RESOURCE_YIELD, inner.bytes());
        }
    }
    {
        std::vector<std::string> access = sorted_strings(p.access_constraints);
        for (i = 0u; i < access.size(); ++i) {
            if (!access[i].empty()) {
                w.add_string(CORE_DATA_MECH_SITE_TAG_ACCESS_CONSTRAINT, access[i]);
            }
        }
    }
    out = w.bytes();
    return true;
}

static bool build_sim_payload_astro_body(const CoredataAstroBody& b,
                                         std::vector<unsigned char>& out) {
    dom::core_tlv::TlvWriter w;
    w.add_string(CORE_DATA_ASTRO_TAG_ID, b.id);
    w.add_u64(CORE_DATA_ASTRO_TAG_ID_HASH, b.id_hash);
    if (b.has_radius) {
        w.add_u64(CORE_DATA_ASTRO_TAG_RADIUS_M, b.radius_m);
    }
    w.add_u64(CORE_DATA_ASTRO_TAG_MU_MANTISSA, b.mu_mantissa);
    w.add_i32(CORE_DATA_ASTRO_TAG_MU_EXP10, b.mu_exp10);
    if (b.has_rotation_rate) {
        w.add_i32(CORE_DATA_ASTRO_TAG_ROT_RATE_Q16, b.rotation_rate_q16);
    }
    if (!b.atmosphere_profile_id.empty()) {
        w.add_string(CORE_DATA_ASTRO_TAG_ATMOS_PROFILE_ID, b.atmosphere_profile_id);
    }
    out = w.bytes();
    return true;
}

} // namespace

namespace {

static bool parse_pack_meta(const unsigned char* data,
                            u32 len,
                            CoredataState& out_state,
                            std::string& err) {
    dom::core_tlv::TlvReader r(data, len);
    dom::core_tlv::TlvRecord rec;
    bool has_schema = false;
    bool has_pack_id = false;
    bool has_ver = false;
    bool has_hash = false;

    while (r.next(rec)) {
        switch (rec.tag) {
        case CORE_DATA_META_TAG_PACK_SCHEMA_VERSION:
            if (read_u32(rec, out_state.pack_schema_version)) {
                has_schema = true;
            }
            break;
        case CORE_DATA_META_TAG_PACK_ID:
            out_state.pack_id = read_string(rec);
            has_pack_id = !out_state.pack_id.empty();
            break;
        case CORE_DATA_META_TAG_PACK_VERSION_NUM:
            if (read_u32(rec, out_state.pack_version_num)) {
                has_ver = true;
            }
            break;
        case CORE_DATA_META_TAG_PACK_VERSION_STR:
            out_state.pack_version_str = read_string(rec);
            break;
        case CORE_DATA_META_TAG_CONTENT_HASH:
            if (read_u64(rec, out_state.content_hash)) {
                has_hash = true;
            }
            break;
        default:
            err = "pack_meta_unknown_tag";
            return false;
        }
    }

    if (r.remaining() != 0u) {
        err = "pack_meta_truncated";
        return false;
    }
    if (!has_schema || !has_pack_id || !has_ver || !has_hash) {
        err = "pack_meta_missing_field";
        return false;
    }
    return true;
}

static bool parse_anchor_record(const std::vector<unsigned char>& payload,
                                CoredataAnchor& out,
                                std::string& err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_kind = false;
    bool has_system_class = false;
    bool has_region_type = false;
    bool has_evidence = false;
    bool has_profile = false;
    bool has_weight = false;
    u64 computed = 0ull;

    out = CoredataAnchor();

    while (r.next(rec)) {
        switch (rec.tag) {
        case CORE_DATA_ANCHOR_TAG_ID:
            out.id = read_string(rec);
            has_id = !out.id.empty();
            break;
        case CORE_DATA_ANCHOR_TAG_ID_HASH:
            has_id_hash = read_u64(rec, out.id_hash);
            break;
        case CORE_DATA_ANCHOR_TAG_KIND:
            has_kind = read_u32(rec, out.kind);
            break;
        case CORE_DATA_ANCHOR_TAG_DISPLAY_NAME:
            out.display_name = read_string(rec);
            break;
        case CORE_DATA_ANCHOR_TAG_SYSTEM_CLASS:
            has_system_class = read_u32(rec, out.system_class);
            break;
        case CORE_DATA_ANCHOR_TAG_REGION_TYPE:
            has_region_type = read_u32(rec, out.region_type);
            break;
        case CORE_DATA_ANCHOR_TAG_EVIDENCE_GRADE:
            has_evidence = read_u32(rec, out.evidence_grade);
            break;
        case CORE_DATA_ANCHOR_TAG_MECH_PROFILE_ID:
            out.mechanics_profile_id = read_string(rec);
            has_profile = !out.mechanics_profile_id.empty();
            break;
        case CORE_DATA_ANCHOR_TAG_ANCHOR_WEIGHT:
            has_weight = read_u32(rec, out.anchor_weight);
            break;
        case CORE_DATA_ANCHOR_TAG_TAG:
            (void)read_string(rec);
            break;
        case CORE_DATA_ANCHOR_TAG_PRESENTATION_POS:
            if (rec.len != 12u) {
                err = "anchor_present_pos_invalid";
                return false;
            }
            if (!dom::core_tlv::tlv_read_i32_le(rec.payload + 0u, 4u, out.present_pos_q16[0]) ||
                !dom::core_tlv::tlv_read_i32_le(rec.payload + 4u, 4u, out.present_pos_q16[1]) ||
                !dom::core_tlv::tlv_read_i32_le(rec.payload + 8u, 4u, out.present_pos_q16[2])) {
                err = "anchor_present_pos_invalid";
                return false;
            }
            out.has_present_pos = true;
            break;
        default:
            err = "anchor_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "anchor_truncated";
        return false;
    }
    if (!has_id || !has_id_hash || !has_kind || !has_evidence || !has_profile || !has_weight) {
        err = "anchor_missing_field";
        return false;
    }
    if (out.kind == CORE_DATA_KIND_SYSTEM && !has_system_class) {
        err = "anchor_missing_system_class";
        return false;
    }
    if (out.kind == CORE_DATA_KIND_REGION && !has_region_type) {
        err = "anchor_missing_region_type";
        return false;
    }
    if (!id_hash64(out.id, computed) || computed != out.id_hash) {
        err = "anchor_id_hash_mismatch";
        return false;
    }
    if (!id_hash64(out.mechanics_profile_id, out.mechanics_profile_id_hash)) {
        err = "anchor_mech_profile_hash_failed";
        return false;
    }
    return true;
}

static bool parse_edge_record(const std::vector<unsigned char>& payload,
                              CoredataEdge& out,
                              std::string& err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_src = false;
    bool has_src_hash = false;
    bool has_dst = false;
    bool has_dst_hash = false;
    bool has_duration = false;
    bool has_cost = false;
    bool has_cost_hash = false;
    u64 computed = 0ull;

    out = CoredataEdge();

    while (r.next(rec)) {
        switch (rec.tag) {
        case CORE_DATA_EDGE_TAG_SRC_ID:
            out.src_id = read_string(rec);
            has_src = !out.src_id.empty();
            break;
        case CORE_DATA_EDGE_TAG_SRC_ID_HASH:
            has_src_hash = read_u64(rec, out.src_id_hash);
            break;
        case CORE_DATA_EDGE_TAG_DST_ID:
            out.dst_id = read_string(rec);
            has_dst = !out.dst_id.empty();
            break;
        case CORE_DATA_EDGE_TAG_DST_ID_HASH:
            has_dst_hash = read_u64(rec, out.dst_id_hash);
            break;
        case CORE_DATA_EDGE_TAG_DURATION_TICKS:
            has_duration = read_u64(rec, out.duration_ticks);
            break;
        case CORE_DATA_EDGE_TAG_COST_PROFILE_ID:
            out.cost_profile_id = read_string(rec);
            has_cost = !out.cost_profile_id.empty();
            break;
        case CORE_DATA_EDGE_TAG_COST_PROFILE_HASH:
            has_cost_hash = read_u64(rec, out.cost_profile_id_hash);
            break;
        case CORE_DATA_EDGE_TAG_HAZARD_PROFILE_ID:
            out.hazard_profile_id = read_string(rec);
            out.has_hazard = !out.hazard_profile_id.empty();
            break;
        case CORE_DATA_EDGE_TAG_HAZARD_PROFILE_HASH:
            out.has_hazard = read_u64(rec, out.hazard_profile_id_hash);
            break;
        default:
            err = "edge_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "edge_truncated";
        return false;
    }
    if (!has_src || !has_src_hash || !has_dst || !has_dst_hash ||
        !has_duration || !has_cost || !has_cost_hash) {
        err = "edge_missing_field";
        return false;
    }
    if (out.duration_ticks == 0ull) {
        err = "edge_duration_invalid";
        return false;
    }
    if (!id_hash64(out.src_id, computed) || computed != out.src_id_hash) {
        err = "edge_src_hash_mismatch";
        return false;
    }
    if (!id_hash64(out.dst_id, computed) || computed != out.dst_id_hash) {
        err = "edge_dst_hash_mismatch";
        return false;
    }
    if (!id_hash64(out.cost_profile_id, computed) || computed != out.cost_profile_id_hash) {
        err = "edge_cost_hash_mismatch";
        return false;
    }
    if (out.has_hazard) {
        if (!id_hash64(out.hazard_profile_id, computed) ||
            computed != out.hazard_profile_id_hash) {
            err = "edge_hazard_hash_mismatch";
            return false;
        }
    }
    return true;
}

static bool parse_rules_entry(const unsigned char* payload,
                              u32 len,
                              CoredataRulesEntry& out,
                              std::string& err) {
    dom::core_tlv::TlvReader r(payload, len);
    dom::core_tlv::TlvRecord rec;
    bool has_region = false;
    bool has_value = false;
    out = CoredataRulesEntry();
    while (r.next(rec)) {
        if (rec.tag == CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE) {
            has_region = read_u32(rec, out.region_type);
        } else if (rec.tag == CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16) {
            has_value = read_i32(rec, out.value_q16);
        } else {
            err = "rules_entry_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "rules_entry_truncated";
        return false;
    }
    if (!has_region || !has_value) {
        err = "rules_entry_missing_field";
        return false;
    }
    return true;
}

static bool parse_rules_record(const std::vector<unsigned char>& payload,
                               CoredataProceduralRules& out,
                               std::string& err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_sys_min = false;
    bool has_sys_max = false;
    bool has_red = false;
    bool has_bin = false;
    bool has_exotic = false;

    out = CoredataProceduralRules();
    out.present = true;

    while (r.next(rec)) {
        switch (rec.tag) {
        case CORE_DATA_RULES_TAG_SYS_MIN:
            has_sys_min = read_u32(rec, out.systems_per_anchor_min);
            break;
        case CORE_DATA_RULES_TAG_SYS_MAX:
            has_sys_max = read_u32(rec, out.systems_per_anchor_max);
            break;
        case CORE_DATA_RULES_TAG_RED_DWARF_RATIO:
            has_red = read_i32(rec, out.red_dwarf_ratio_q16);
            break;
        case CORE_DATA_RULES_TAG_BINARY_RATIO:
            has_bin = read_i32(rec, out.binary_ratio_q16);
            break;
        case CORE_DATA_RULES_TAG_EXOTIC_RATIO:
            has_exotic = read_i32(rec, out.exotic_ratio_q16);
            break;
        case CORE_DATA_RULES_TAG_CLUSTER_DENSITY:
        case CORE_DATA_RULES_TAG_METALLICITY_BIAS:
        case CORE_DATA_RULES_TAG_HAZARD_FREQUENCY: {
            CoredataRulesEntry entry;
            if (!parse_rules_entry(rec.payload, rec.len, entry, err)) {
                return false;
            }
            if (rec.tag == CORE_DATA_RULES_TAG_CLUSTER_DENSITY) {
                out.cluster_density.push_back(entry);
            } else if (rec.tag == CORE_DATA_RULES_TAG_METALLICITY_BIAS) {
                out.metallicity_bias.push_back(entry);
            } else {
                out.hazard_frequency.push_back(entry);
            }
            break;
        }
        default:
            err = "rules_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "rules_truncated";
        return false;
    }
    if (!has_sys_min || !has_sys_max || !has_red || !has_bin || !has_exotic) {
        err = "rules_missing_field";
        return false;
    }
    return true;
}

static bool parse_system_profile_record(const std::vector<unsigned char>& payload,
                                        CoredataSystemProfile& out,
                                        std::string& err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_nav = false;
    bool has_debris = false;
    bool has_rad = false;
    bool has_warp = false;
    bool has_survey = false;
    u64 computed = 0ull;

    out = CoredataSystemProfile();

    while (r.next(rec)) {
        switch (rec.tag) {
        case CORE_DATA_MECH_SYS_TAG_ID:
            out.id = read_string(rec);
            has_id = !out.id.empty();
            break;
        case CORE_DATA_MECH_SYS_TAG_ID_HASH:
            has_id_hash = read_u64(rec, out.id_hash);
            break;
        case CORE_DATA_MECH_SYS_TAG_NAV_INSTABILITY:
            has_nav = read_i32(rec, out.navigation_instability_q16);
            break;
        case CORE_DATA_MECH_SYS_TAG_DEBRIS_COLLISION:
            has_debris = read_i32(rec, out.debris_collision_q16);
            break;
        case CORE_DATA_MECH_SYS_TAG_RADIATION_BASELINE:
            has_rad = read_i32(rec, out.radiation_baseline_q16);
            break;
        case CORE_DATA_MECH_SYS_TAG_WARP_CAP:
            has_warp = read_i32(rec, out.warp_cap_modifier_q16);
            break;
        case CORE_DATA_MECH_SYS_TAG_SURVEY_DIFFICULTY:
            has_survey = read_i32(rec, out.survey_difficulty_q16);
            break;
        case CORE_DATA_MECH_SYS_TAG_SUPERNOVA_TICKS:
            out.has_supernova = read_u64(rec, out.supernova_timer_ticks);
            break;
        default:
            err = "mech_system_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "mech_system_truncated";
        return false;
    }
    if (!has_id || !has_id_hash || !has_nav || !has_debris || !has_rad ||
        !has_warp || !has_survey) {
        err = "mech_system_missing_field";
        return false;
    }
    if (!id_hash64(out.id, computed) || computed != out.id_hash) {
        err = "mech_system_id_hash_mismatch";
        return false;
    }
    return true;
}

} // namespace

namespace {

static u64 hash_record(u32 type_id, u16 version, const std::vector<unsigned char>& payload) {
    unsigned char header[8];
    dom::core_tlv::tlv_write_u32_le(header, type_id);
    dom::core_tlv::tlv_write_u32_le(header + 4u, (u32)version);
    std::vector<unsigned char> tmp;
    tmp.reserve(sizeof(header) + payload.size());
    tmp.insert(tmp.end(), header, header + sizeof(header));
    if (!payload.empty()) {
        tmp.insert(tmp.end(), payload.begin(), payload.end());
    }
    return dom::core_tlv::tlv_fnv1a64(tmp.empty() ? 0 : &tmp[0], tmp.size());
}

struct RecordView {
    u32 type_id;
    std::string id;
    u64 id_hash;
    std::vector<unsigned char> payload;
    u64 record_hash;
};

static bool record_less(const RecordView& a, const RecordView& b) {
    if (a.type_id != b.type_id) {
        return a.type_id < b.type_id;
    }
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static u64 hash_content(const std::vector<RecordView>& records) {
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

static bool record_is_canonical(const std::vector<RecordView>& records) {
    size_t i;
    for (i = 1u; i < records.size(); ++i) {
        if (record_less(records[i], records[i - 1u])) {
            return false;
        }
    }
    return true;
}

struct CoredataAnchor {
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

    CoredataAnchor()
        : id(),
          id_hash(0ull),
          kind(0u),
          system_class(0u),
          region_type(0u),
          evidence_grade(0u),
          mechanics_profile_id(),
          mechanics_profile_id_hash(0ull),
          anchor_weight(0u),
          display_name(),
          has_present_pos(false) {
        present_pos_q16[0] = 0;
        present_pos_q16[1] = 0;
        present_pos_q16[2] = 0;
    }
};

struct CoredataEdge {
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

    CoredataEdge()
        : src_id(),
          src_id_hash(0ull),
          dst_id(),
          dst_id_hash(0ull),
          duration_ticks(0ull),
          cost_profile_id(),
          cost_profile_id_hash(0ull),
          hazard_profile_id(),
          hazard_profile_id_hash(0ull),
          has_hazard(false) {}
};

struct CoredataRulesEntry {
    u32 region_type;
    i32 value_q16;

    CoredataRulesEntry() : region_type(0u), value_q16(0) {}
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

    CoredataProceduralRules()
        : present(false),
          systems_per_anchor_min(0u),
          systems_per_anchor_max(0u),
          red_dwarf_ratio_q16(0),
          binary_ratio_q16(0),
          exotic_ratio_q16(0),
          cluster_density(),
          metallicity_bias(),
          hazard_frequency() {}
};

struct CoredataSystemProfile {
    std::string id;
    u64 id_hash;
    i32 navigation_instability_q16;
    i32 debris_collision_q16;
    i32 radiation_baseline_q16;
    i32 warp_cap_modifier_q16;
    i32 survey_difficulty_q16;
    u64 supernova_timer_ticks;
    bool has_supernova;

    CoredataSystemProfile()
        : id(),
          id_hash(0ull),
          navigation_instability_q16(0),
          debris_collision_q16(0),
          radiation_baseline_q16(0),
          warp_cap_modifier_q16(0),
          survey_difficulty_q16(0),
          supernova_timer_ticks(0ull),
          has_supernova(false) {}
};

struct CoredataResourceModifier {
    std::string resource_id;
    u64 resource_id_hash;
    i32 modifier_q16;

    CoredataResourceModifier()
        : resource_id(),
          resource_id_hash(0ull),
          modifier_q16(0) {}
};

struct CoredataSiteProfile {
    std::string id;
    u64 id_hash;
    i32 hazard_radiation_q16;
    i32 hazard_pressure_q16;
    i32 corrosion_rate_q16;
    i32 temperature_extreme_q16;
    std::vector<CoredataResourceModifier> resource_yield;
    std::vector<std::string> access_constraints;

    CoredataSiteProfile()
        : id(),
          id_hash(0ull),
          hazard_radiation_q16(0),
          hazard_pressure_q16(0),
          corrosion_rate_q16(0),
          temperature_extreme_q16(0),
          resource_yield(),
          access_constraints() {}
};

struct CoredataAstroBody {
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

    CoredataAstroBody()
        : id(),
          id_hash(0ull),
          has_radius(false),
          radius_m(0ull),
          mu_mantissa(0ull),
          mu_exp10(0),
          has_rotation_rate(false),
          rotation_rate_q16(0),
          atmosphere_profile_id(),
          atmosphere_profile_id_hash(0ull) {}
};

struct CoredataState {
    u32 pack_schema_version;
    std::string pack_id;
    u32 pack_version_num;
    std::string pack_version_str;
    u64 content_hash;
    u64 sim_digest;
    std::vector<CoredataAnchor> anchors;
    std::vector<CoredataEdge> edges;
    CoredataProceduralRules rules;
    std::vector<CoredataSystemProfile> system_profiles;
    std::vector<CoredataSiteProfile> site_profiles;
    std::vector<CoredataAstroBody> astro_bodies;

    CoredataState()
        : pack_schema_version(0u),
          pack_id(),
          pack_version_num(0u),
          pack_version_str(),
          content_hash(0ull),
          sim_digest(0ull),
          anchors(),
          edges(),
          rules(),
          system_profiles(),
          site_profiles(),
          astro_bodies() {}
};

} // namespace

namespace {

static bool parse_resource_modifier(const unsigned char* payload,
                                    u32 len,
                                    CoredataResourceModifier& out,
                                    std::string& err) {
    dom::core_tlv::TlvReader r(payload, len);
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_mod = false;
    u64 computed = 0ull;
    out = CoredataResourceModifier();

    while (r.next(rec)) {
        if (rec.tag == CORE_DATA_MECH_SITE_RES_TAG_ID) {
            out.resource_id = read_string(rec);
            has_id = !out.resource_id.empty();
        } else if (rec.tag == CORE_DATA_MECH_SITE_RES_TAG_MOD_Q16) {
            has_mod = read_i32(rec, out.modifier_q16);
        } else {
            err = "mech_site_resource_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "mech_site_resource_truncated";
        return false;
    }
    if (!has_id || !has_mod) {
        err = "mech_site_resource_missing_field";
        return false;
    }
    if (!id_hash64(out.resource_id, computed)) {
        err = "mech_site_resource_hash_failed";
        return false;
    }
    out.resource_id_hash = computed;
    return true;
}

static bool parse_site_profile_record(const std::vector<unsigned char>& payload,
                                      CoredataSiteProfile& out,
                                      std::string& err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_rad = false;
    bool has_press = false;
    bool has_corrosion = false;
    bool has_temp = false;
    u64 computed = 0ull;

    out = CoredataSiteProfile();

    while (r.next(rec)) {
        switch (rec.tag) {
        case CORE_DATA_MECH_SITE_TAG_ID:
            out.id = read_string(rec);
            has_id = !out.id.empty();
            break;
        case CORE_DATA_MECH_SITE_TAG_ID_HASH:
            has_id_hash = read_u64(rec, out.id_hash);
            break;
        case CORE_DATA_MECH_SITE_TAG_HAZARD_RAD:
            has_rad = read_i32(rec, out.hazard_radiation_q16);
            break;
        case CORE_DATA_MECH_SITE_TAG_HAZARD_PRESS:
            has_press = read_i32(rec, out.hazard_pressure_q16);
            break;
        case CORE_DATA_MECH_SITE_TAG_CORROSION_RATE:
            has_corrosion = read_i32(rec, out.corrosion_rate_q16);
            break;
        case CORE_DATA_MECH_SITE_TAG_TEMP_EXTREME:
            has_temp = read_i32(rec, out.temperature_extreme_q16);
            break;
        case CORE_DATA_MECH_SITE_TAG_RESOURCE_YIELD: {
            CoredataResourceModifier mod;
            if (!parse_resource_modifier(rec.payload, rec.len, mod, err)) {
                return false;
            }
            out.resource_yield.push_back(mod);
            break;
        }
        case CORE_DATA_MECH_SITE_TAG_ACCESS_CONSTRAINT:
            out.access_constraints.push_back(read_string(rec));
            break;
        default:
            err = "mech_site_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "mech_site_truncated";
        return false;
    }
    if (!has_id || !has_id_hash || !has_rad || !has_press || !has_corrosion || !has_temp) {
        err = "mech_site_missing_field";
        return false;
    }
    if (!id_hash64(out.id, computed) || computed != out.id_hash) {
        err = "mech_site_id_hash_mismatch";
        return false;
    }
    return true;
}

static bool parse_astro_body_record(const std::vector<unsigned char>& payload,
                                    CoredataAstroBody& out,
                                    std::string& err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_mu = false;
    bool has_exp = false;
    u64 computed = 0ull;

    out = CoredataAstroBody();

    while (r.next(rec)) {
        switch (rec.tag) {
        case CORE_DATA_ASTRO_TAG_ID:
            out.id = read_string(rec);
            has_id = !out.id.empty();
            break;
        case CORE_DATA_ASTRO_TAG_ID_HASH:
            has_id_hash = read_u64(rec, out.id_hash);
            break;
        case CORE_DATA_ASTRO_TAG_RADIUS_M:
            out.has_radius = read_u64(rec, out.radius_m);
            break;
        case CORE_DATA_ASTRO_TAG_MU_MANTISSA:
            has_mu = read_u64(rec, out.mu_mantissa);
            break;
        case CORE_DATA_ASTRO_TAG_MU_EXP10:
            has_exp = read_i32(rec, out.mu_exp10);
            break;
        case CORE_DATA_ASTRO_TAG_ROT_RATE_Q16:
            out.has_rotation_rate = read_i32(rec, out.rotation_rate_q16);
            break;
        case CORE_DATA_ASTRO_TAG_ATMOS_PROFILE_ID:
            out.atmosphere_profile_id = read_string(rec);
            if (!out.atmosphere_profile_id.empty()) {
                if (!id_hash64(out.atmosphere_profile_id, out.atmosphere_profile_id_hash)) {
                    err = "astro_atmos_profile_hash_failed";
                    return false;
                }
            }
            break;
        default:
            err = "astro_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "astro_truncated";
        return false;
    }
    if (!has_id || !has_id_hash || !has_mu || !has_exp) {
        err = "astro_missing_field";
        return false;
    }
    if (!id_hash64(out.id, computed) || computed != out.id_hash) {
        err = "astro_id_hash_mismatch";
        return false;
    }
    return true;
}

} // namespace

namespace {

static u64 compute_sim_digest(const CoredataState& state) {
    std::vector<RecordView> entries;
    std::vector<unsigned char> payload;
    size_t i;

    entries.reserve(state.anchors.size() +
                    state.edges.size() +
                    state.system_profiles.size() +
                    state.site_profiles.size() +
                    state.astro_bodies.size() +
                    (state.rules.present ? 1u : 0u));

    for (i = 0u; i < state.anchors.size(); ++i) {
        RecordView v;
        if (!build_sim_payload_anchor(state.anchors[i], payload)) {
            continue;
        }
        v.type_id = CORE_DATA_REC_COSMO_ANCHOR;
        v.id = state.anchors[i].id;
        v.id_hash = state.anchors[i].id_hash;
        v.payload = payload;
        v.record_hash = hash_record(v.type_id, CORE_DATA_REC_VERSION_V1, v.payload);
        entries.push_back(v);
    }
    for (i = 0u; i < state.edges.size(); ++i) {
        RecordView v;
        if (!build_sim_payload_edge(state.edges[i], payload)) {
            continue;
        }
        v.type_id = CORE_DATA_REC_COSMO_EDGE;
        v.id_hash = compute_edge_key_hash(state.edges[i]);
        v.id = state.edges[i].src_id + "->" + state.edges[i].dst_id;
        v.payload = payload;
        v.record_hash = hash_record(v.type_id, CORE_DATA_REC_VERSION_V1, v.payload);
        entries.push_back(v);
    }
    if (state.rules.present) {
        RecordView v;
        if (build_sim_payload_rules(state.rules, payload)) {
            v.type_id = CORE_DATA_REC_COSMO_RULES;
            v.id.clear();
            v.id_hash = 0ull;
            v.payload = payload;
            v.record_hash = hash_record(v.type_id, CORE_DATA_REC_VERSION_V1, v.payload);
            entries.push_back(v);
        }
    }
    for (i = 0u; i < state.system_profiles.size(); ++i) {
        RecordView v;
        if (!build_sim_payload_system_profile(state.system_profiles[i], payload)) {
            continue;
        }
        v.type_id = CORE_DATA_REC_MECH_SYSTEM;
        v.id = state.system_profiles[i].id;
        v.id_hash = state.system_profiles[i].id_hash;
        v.payload = payload;
        v.record_hash = hash_record(v.type_id, CORE_DATA_REC_VERSION_V1, v.payload);
        entries.push_back(v);
    }
    for (i = 0u; i < state.site_profiles.size(); ++i) {
        RecordView v;
        if (!build_sim_payload_site_profile(state.site_profiles[i], payload)) {
            continue;
        }
        v.type_id = CORE_DATA_REC_MECH_SITE;
        v.id = state.site_profiles[i].id;
        v.id_hash = state.site_profiles[i].id_hash;
        v.payload = payload;
        v.record_hash = hash_record(v.type_id, CORE_DATA_REC_VERSION_V1, v.payload);
        entries.push_back(v);
    }
    for (i = 0u; i < state.astro_bodies.size(); ++i) {
        RecordView v;
        if (!build_sim_payload_astro_body(state.astro_bodies[i], payload)) {
            continue;
        }
        v.type_id = CORE_DATA_REC_ASTRO_BODY;
        v.id = state.astro_bodies[i].id;
        v.id_hash = state.astro_bodies[i].id_hash;
        v.payload = payload;
        v.record_hash = hash_record(v.type_id, CORE_DATA_REC_VERSION_V1, v.payload);
        entries.push_back(v);
    }

    std::sort(entries.begin(), entries.end(), record_less);
    return hash_content(entries);
}

static bool apply_rules_sorted(std::vector<CoredataRulesEntry>& entries) {
    if (entries.empty()) {
        return true;
    }
    std::sort(entries.begin(), entries.end(), rules_entry_less);
    return true;
}

static bool load_coredata_from_bytes(const unsigned char* data,
                                     size_t size,
                                     CoredataState& out_state,
                                     std::string& out_error) {
    dom::core_tlv::TlvReader r(data, size);
    dom::core_tlv::TlvRecord rec;
    std::vector<RecordView> records;
    std::vector<RecordView> content_records;
    bool have_meta = false;
    bool have_rules = false;
    size_t i;

    out_state = CoredataState();

    while (r.next(rec)) {
        RecordView view;
        view.type_id = rec.tag;
        view.id.clear();
        view.id_hash = 0ull;
        view.payload.clear();
        if (rec.len > 0u && rec.payload) {
            view.payload.assign(rec.payload, rec.payload + rec.len);
        }
        view.record_hash = hash_record(view.type_id, (u16)CORE_DATA_REC_VERSION_V1, view.payload);

        if (view.type_id == CORE_DATA_REC_PACK_META) {
            if (have_meta) {
                out_error = "pack_meta_duplicate";
                return false;
            }
            if (!parse_pack_meta(rec.payload, rec.len, out_state, out_error)) {
                return false;
            }
            have_meta = true;
        } else if (view.type_id == CORE_DATA_REC_COSMO_ANCHOR) {
            CoredataAnchor anchor;
            if (!parse_anchor_record(view.payload, anchor, out_error)) {
                return false;
            }
            view.id = anchor.id;
            view.id_hash = anchor.id_hash;
            out_state.anchors.push_back(anchor);
        } else if (view.type_id == CORE_DATA_REC_COSMO_EDGE) {
            CoredataEdge edge;
            if (!parse_edge_record(view.payload, edge, out_error)) {
                return false;
            }
            view.id = edge.src_id + "->" + edge.dst_id;
            view.id_hash = compute_edge_key_hash(edge);
            out_state.edges.push_back(edge);
        } else if (view.type_id == CORE_DATA_REC_COSMO_RULES) {
            if (have_rules) {
                out_error = "rules_multiple";
                return false;
            }
            if (!parse_rules_record(view.payload, out_state.rules, out_error)) {
                return false;
            }
            view.id.clear();
            view.id_hash = 0ull;
            have_rules = true;
        } else if (view.type_id == CORE_DATA_REC_MECH_SYSTEM) {
            CoredataSystemProfile prof;
            if (!parse_system_profile_record(view.payload, prof, out_error)) {
                return false;
            }
            view.id = prof.id;
            view.id_hash = prof.id_hash;
            out_state.system_profiles.push_back(prof);
        } else if (view.type_id == CORE_DATA_REC_MECH_SITE) {
            CoredataSiteProfile prof;
            if (!parse_site_profile_record(view.payload, prof, out_error)) {
                return false;
            }
            view.id = prof.id;
            view.id_hash = prof.id_hash;
            out_state.site_profiles.push_back(prof);
        } else if (view.type_id == CORE_DATA_REC_ASTRO_BODY) {
            CoredataAstroBody body;
            if (!parse_astro_body_record(view.payload, body, out_error)) {
                return false;
            }
            view.id = body.id;
            view.id_hash = body.id_hash;
            out_state.astro_bodies.push_back(body);
        } else {
            out_error = "record_unknown_type";
            return false;
        }

        records.push_back(view);
        if (view.type_id != CORE_DATA_REC_PACK_META) {
            content_records.push_back(view);
        }
    }

    if (r.remaining() != 0u) {
        out_error = "pack_truncated";
        return false;
    }
    if (!have_meta) {
        out_error = "pack_meta_missing";
        return false;
    }
    if (out_state.anchors.empty() || out_state.system_profiles.empty() ||
        out_state.site_profiles.empty() || out_state.astro_bodies.empty() ||
        !out_state.rules.present) {
        out_error = "required_records_missing";
        return false;
    }
    if (!record_is_canonical(records)) {
        out_error = "record_order_invalid";
        return false;
    }

    std::sort(content_records.begin(), content_records.end(), record_less);
    if (out_state.content_hash != hash_content(content_records)) {
        out_error = "content_hash_mismatch";
        return false;
    }

    for (i = 0u; i < content_records.size(); ++i) {
        if (i > 0u && record_less(content_records[i], content_records[i - 1u])) {
            out_error = "content_record_order_invalid";
            return false;
        }
        if (i > 0u && content_records[i].type_id == content_records[i - 1u].type_id &&
            content_records[i].id_hash == content_records[i - 1u].id_hash &&
            content_records[i].id == content_records[i - 1u].id) {
            out_error = "duplicate_record_id";
            return false;
        }
    }

    {
        std::vector<u64> mech_profile_hashes;
        for (i = 0u; i < out_state.system_profiles.size(); ++i) {
            mech_profile_hashes.push_back(out_state.system_profiles[i].id_hash);
        }
        for (i = 0u; i < out_state.anchors.size(); ++i) {
            bool found = false;
            size_t j;
            for (j = 0u; j < mech_profile_hashes.size(); ++j) {
                if (mech_profile_hashes[j] == out_state.anchors[i].mechanics_profile_id_hash) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                out_error = "anchor_mechanics_profile_missing";
                return false;
            }
        }
    }

    {
        std::vector<u64> anchor_ids;
        anchor_ids.reserve(out_state.anchors.size());
        for (i = 0u; i < out_state.anchors.size(); ++i) {
            anchor_ids.push_back(out_state.anchors[i].id_hash);
        }
        for (i = 0u; i < out_state.edges.size(); ++i) {
            bool src_ok = false;
            bool dst_ok = false;
            size_t j;
            for (j = 0u; j < anchor_ids.size(); ++j) {
                if (anchor_ids[j] == out_state.edges[i].src_id_hash) {
                    src_ok = true;
                }
                if (anchor_ids[j] == out_state.edges[i].dst_id_hash) {
                    dst_ok = true;
                }
                if (src_ok && dst_ok) {
                    break;
                }
            }
            if (!src_ok || !dst_ok) {
                out_error = "edge_missing_anchor";
                return false;
            }
        }
    }

    if (out_state.rules.present) {
        apply_rules_sorted(out_state.rules.cluster_density);
        apply_rules_sorted(out_state.rules.metallicity_bias);
        apply_rules_sorted(out_state.rules.hazard_frequency);
    }

    out_state.sim_digest = compute_sim_digest(out_state);
    return true;
}

} // namespace

bool launcher_coredata_sim_hash_from_manifest(const dom::launcher_core::LauncherInstanceManifest& manifest,
                                              const std::string& state_root,
                                              u64& out_hash,
                                              std::string& out_error) {
    size_t i;
    u32 version_num = 0u;
    std::string version_err;
    std::string pack_id;
    std::string version_str;
    std::string pack_path;
    std::vector<unsigned char> bytes;
    CoredataState state;

    out_hash = 0ull;
    out_error.clear();

    if (state_root.empty()) {
        out_error = "state_root_missing";
        return false;
    }

    for (i = 0u; i < manifest.content_entries.size(); ++i) {
        const dom::launcher_core::LauncherContentEntry& e = manifest.content_entries[i];
        if (!is_coredata_pack_id(e.id)) {
            continue;
        }
        if (e.enabled == 0u) {
            out_error = "coredata_pack_disabled";
            return false;
        }
        pack_id = e.id;
        version_str = e.version;
        break;
    }
    if (pack_id.empty()) {
        out_error = "coredata_pack_missing";
        return false;
    }
    if (version_str.empty()) {
        out_error = "coredata_pack_version_missing";
        return false;
    }
    if (!parse_version_num(version_str, version_num, version_err)) {
        out_error = std::string("coredata_pack_version_invalid;") + version_err;
        return false;
    }

    {
        const std::string packs_root = path_join(path_join(state_root, "repo"), "packs");
        const std::string pack_root = path_join(packs_root, pack_id);
        const std::string version_dir = format_version_dir(version_num);
        const std::string out_dir = path_join(pack_root, version_dir);
        pack_path = path_join(out_dir, "pack.tlv");
    }

    if (!read_file_all(pack_path, bytes)) {
        out_error = "coredata_pack_read_failed";
        return false;
    }
    if (!load_coredata_from_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0],
                                  bytes.size(),
                                  state,
                                  out_error)) {
        return false;
    }
    if (!state.pack_id.empty() && !str_ieq(state.pack_id, pack_id.c_str())) {
        out_error = "coredata_pack_id_mismatch";
        return false;
    }
    if (state.pack_version_num != 0u && state.pack_version_num != version_num) {
        out_error = "coredata_pack_version_mismatch";
        return false;
    }

    out_hash = state.sim_digest;
    return true;
}

} // namespace dom
