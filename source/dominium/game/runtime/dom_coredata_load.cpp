/*
FILE: source/dominium/game/runtime/dom_coredata_load.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/coredata_load
RESPONSIBILITY: Loads coredata TLV packs and applies them to runtime registries.
*/
#include "runtime/dom_coredata_load.h"

#include <algorithm>
#include <fstream>
#include <sstream>

#include "dominium/core_tlv.h"
#include "runtime/dom_io_guard.h"

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

static void set_error(std::string *out, const char *msg) {
    if (out) {
        out->assign(msg ? msg : "");
    }
}

static bool read_file_bytes(const char *path,
                            std::vector<unsigned char> &out,
                            std::string &err) {
    std::ifstream in;
    std::streamoff size;
    if (!path || !path[0]) {
        err = "path_empty";
        return false;
    }
    if (!dom_io_guard_io_allowed()) {
        dom_io_guard_note_violation("coredata_read", path);
        err = "io_not_allowed";
        return false;
    }
    in.open(path, std::ios::in | std::ios::binary);
    if (!in) {
        err = "open_failed";
        return false;
    }
    in.seekg(0, std::ios::end);
    size = in.tellg();
    if (size <= 0) {
        err = "empty_file";
        return false;
    }
    in.seekg(0, std::ios::beg);
    out.assign((size_t)size, 0u);
    in.read(reinterpret_cast<char *>(&out[0]), size);
    if (!in.good() && !in.eof()) {
        err = "read_failed";
        return false;
    }
    return true;
}

static bool id_hash64(const std::string &id, u64 &out_hash) {
    if (id.empty()) {
        out_hash = 0ull;
        return false;
    }
    return dom_id_hash64(id.c_str(), (u32)id.size(), &out_hash) == DOM_SPACETIME_OK;
}

static bool read_u32(const dom::core_tlv::TlvRecord &rec, u32 &out) {
    return dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out);
}

static bool read_i32(const dom::core_tlv::TlvRecord &rec, i32 &out) {
    return dom::core_tlv::tlv_read_i32_le(rec.payload, rec.len, out);
}

static bool read_u64(const dom::core_tlv::TlvRecord &rec, u64 &out) {
    return dom::core_tlv::tlv_read_u64_le(rec.payload, rec.len, out);
}

static std::string read_string(const dom::core_tlv::TlvRecord &rec) {
    return dom::core_tlv::tlv_read_string(rec.payload, rec.len);
}

static u64 hash_record(u32 type_id, u16 version, const std::vector<unsigned char> &payload) {
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

static bool record_less(const RecordView &a, const RecordView &b) {
    if (a.type_id != b.type_id) {
        return a.type_id < b.type_id;
    }
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static u64 hash_content(const std::vector<RecordView> &records) {
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

static bool parse_pack_meta(const unsigned char *data,
                            u32 len,
                            dom_coredata_state &out_state,
                            std::string &err) {
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

static bool parse_anchor_record(const std::vector<unsigned char> &payload,
                                dom_coredata_anchor &out,
                                std::string &err) {
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

    out = dom_coredata_anchor();

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

static bool parse_edge_record(const std::vector<unsigned char> &payload,
                              dom_coredata_edge &out,
                              std::string &err) {
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

    out = dom_coredata_edge();

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

static bool parse_rules_entry(const unsigned char *payload,
                              u32 len,
                              dom_coredata_rules_entry &out,
                              std::string &err) {
    dom::core_tlv::TlvReader r(payload, len);
    dom::core_tlv::TlvRecord rec;
    bool has_region = false;
    bool has_value = false;
    out = dom_coredata_rules_entry();
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

static bool parse_rules_record(const std::vector<unsigned char> &payload,
                               dom_coredata_procedural_rules &out,
                               std::string &err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_sys_min = false;
    bool has_sys_max = false;
    bool has_red = false;
    bool has_bin = false;
    bool has_exotic = false;

    out = dom_coredata_procedural_rules();
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
            dom_coredata_rules_entry entry;
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

static bool parse_system_profile_record(const std::vector<unsigned char> &payload,
                                        dom_coredata_system_profile &out,
                                        std::string &err) {
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

    out = dom_coredata_system_profile();

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

static bool parse_resource_modifier(const unsigned char *payload,
                                    u32 len,
                                    dom_coredata_resource_modifier &out,
                                    std::string &err) {
    dom::core_tlv::TlvReader r(payload, len);
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_mod = false;
    u64 computed = 0ull;
    out = dom_coredata_resource_modifier();

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

static bool parse_site_profile_record(const std::vector<unsigned char> &payload,
                                      dom_coredata_site_profile &out,
                                      std::string &err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_rad = false;
    bool has_press = false;
    bool has_corrosion = false;
    bool has_temp = false;
    u64 computed = 0ull;

    out = dom_coredata_site_profile();

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
            dom_coredata_resource_modifier mod;
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

static bool parse_astro_body_record(const std::vector<unsigned char> &payload,
                                    dom_coredata_astro_body &out,
                                    std::string &err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_mu = false;
    bool has_exp = false;
    u64 computed = 0ull;

    out = dom_coredata_astro_body();

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

static bool record_is_canonical(const std::vector<RecordView> &records) {
    size_t i;
    for (i = 1u; i < records.size(); ++i) {
        if (record_less(records[i], records[i - 1u])) {
            return false;
        }
    }
    return true;
}

static u64 compute_edge_key_hash(const dom_coredata_edge &edge) {
    std::string key = edge.src_id + "->" + edge.dst_id;
    u64 hash = 0ull;
    if (dom_id_hash64(key.c_str(), (u32)key.size(), &hash) != DOM_SPACETIME_OK) {
        return 0ull;
    }
    return hash;
}

static bool rules_entry_less(const dom_coredata_rules_entry &a,
                             const dom_coredata_rules_entry &b) {
    return a.region_type < b.region_type;
}

static bool resource_mod_less(const dom_coredata_resource_modifier &a,
                              const dom_coredata_resource_modifier &b) {
    return a.resource_id < b.resource_id;
}

static std::vector<dom_coredata_rules_entry> sorted_rules(const std::vector<dom_coredata_rules_entry> &in) {
    std::vector<dom_coredata_rules_entry> out = in;
    std::sort(out.begin(), out.end(), rules_entry_less);
    return out;
}

static std::vector<dom_coredata_resource_modifier> sorted_resources(const std::vector<dom_coredata_resource_modifier> &in) {
    std::vector<dom_coredata_resource_modifier> out = in;
    std::sort(out.begin(), out.end(), resource_mod_less);
    return out;
}

static std::vector<std::string> sorted_strings(const std::vector<std::string> &in) {
    std::vector<std::string> out = in;
    std::sort(out.begin(), out.end());
    return out;
}

static bool build_sim_payload_anchor(const dom_coredata_anchor &a,
                                     std::vector<unsigned char> &out) {
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

static bool build_sim_payload_edge(const dom_coredata_edge &e,
                                   std::vector<unsigned char> &out) {
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

static bool build_sim_payload_rules(const dom_coredata_procedural_rules &r,
                                    std::vector<unsigned char> &out) {
    dom::core_tlv::TlvWriter w;
    size_t i;
    w.add_u32(CORE_DATA_RULES_TAG_SYS_MIN, r.systems_per_anchor_min);
    w.add_u32(CORE_DATA_RULES_TAG_SYS_MAX, r.systems_per_anchor_max);
    w.add_i32(CORE_DATA_RULES_TAG_RED_DWARF_RATIO, r.red_dwarf_ratio_q16);
    w.add_i32(CORE_DATA_RULES_TAG_BINARY_RATIO, r.binary_ratio_q16);
    w.add_i32(CORE_DATA_RULES_TAG_EXOTIC_RATIO, r.exotic_ratio_q16);
    {
        std::vector<dom_coredata_rules_entry> entries = sorted_rules(r.cluster_density);
        for (i = 0u; i < entries.size(); ++i) {
            dom::core_tlv::TlvWriter inner;
            inner.add_u32(CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE, entries[i].region_type);
            inner.add_i32(CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16, entries[i].value_q16);
            w.add_container(CORE_DATA_RULES_TAG_CLUSTER_DENSITY, inner.bytes());
        }
    }
    {
        std::vector<dom_coredata_rules_entry> entries = sorted_rules(r.metallicity_bias);
        for (i = 0u; i < entries.size(); ++i) {
            dom::core_tlv::TlvWriter inner;
            inner.add_u32(CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE, entries[i].region_type);
            inner.add_i32(CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16, entries[i].value_q16);
            w.add_container(CORE_DATA_RULES_TAG_METALLICITY_BIAS, inner.bytes());
        }
    }
    {
        std::vector<dom_coredata_rules_entry> entries = sorted_rules(r.hazard_frequency);
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

static bool build_sim_payload_system_profile(const dom_coredata_system_profile &p,
                                             std::vector<unsigned char> &out) {
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

static bool build_sim_payload_site_profile(const dom_coredata_site_profile &p,
                                           std::vector<unsigned char> &out) {
    dom::core_tlv::TlvWriter w;
    size_t i;
    w.add_string(CORE_DATA_MECH_SITE_TAG_ID, p.id);
    w.add_u64(CORE_DATA_MECH_SITE_TAG_ID_HASH, p.id_hash);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_HAZARD_RAD, p.hazard_radiation_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_HAZARD_PRESS, p.hazard_pressure_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_CORROSION_RATE, p.corrosion_rate_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_TEMP_EXTREME, p.temperature_extreme_q16);
    {
        std::vector<dom_coredata_resource_modifier> mods = sorted_resources(p.resource_yield);
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

static bool build_sim_payload_astro_body(const dom_coredata_astro_body &b,
                                         std::vector<unsigned char> &out) {
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

static u64 compute_sim_digest(const dom_coredata_state &state) {
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

static bool apply_rules_sorted(std::vector<dom_coredata_rules_entry> &entries) {
    if (entries.empty()) {
        return true;
    }
    std::sort(entries.begin(), entries.end(), rules_entry_less);
    return true;
}

static bool mul_pow10_u64(u64 &value, int exp) {
    int i;
    if (exp < 0) {
        return false;
    }
    for (i = 0; i < exp; ++i) {
        if (value > 0xffffffffffffffffull / 10ull) {
            return false;
        }
        value *= 10ull;
    }
    return true;
}

static bool compute_mu_m3_s2(const dom_coredata_astro_body &body, u64 &out_mu) {
    u64 mu = body.mu_mantissa;
    if (mu == 0ull) {
        return false;
    }
    if (!mul_pow10_u64(mu, body.mu_exp10)) {
        return false;
    }
    out_mu = mu;
    return true;
}

static bool compute_rotation_ticks(i32 rotation_rate_q16, u32 ups, u64 &out_ticks) {
    const i32 two_pi_q16 = 411775;
    u64 period_s_q16;
    u64 ticks;
    if (rotation_rate_q16 <= 0 || ups == 0u) {
        out_ticks = 0ull;
        return false;
    }
    period_s_q16 = (((u64)two_pi_q16) << 16) / (u64)rotation_rate_q16;
    ticks = (period_s_q16 * (u64)ups + 0x8000u) >> 16;
    out_ticks = ticks;
    return true;
}

} // namespace

dom_coredata_anchor::dom_coredata_anchor()
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

dom_coredata_edge::dom_coredata_edge()
    : src_id(),
      src_id_hash(0ull),
      dst_id(),
      dst_id_hash(0ull),
      duration_ticks(0ull),
      cost_profile_id(),
      cost_profile_id_hash(0ull),
      hazard_profile_id(),
      hazard_profile_id_hash(0ull),
      has_hazard(false) {
}

dom_coredata_rules_entry::dom_coredata_rules_entry()
    : region_type(0u),
      value_q16(0) {
}

dom_coredata_procedural_rules::dom_coredata_procedural_rules()
    : present(false),
      systems_per_anchor_min(0u),
      systems_per_anchor_max(0u),
      red_dwarf_ratio_q16(0),
      binary_ratio_q16(0),
      exotic_ratio_q16(0),
      cluster_density(),
      metallicity_bias(),
      hazard_frequency() {
}

dom_coredata_system_profile::dom_coredata_system_profile()
    : id(),
      id_hash(0ull),
      navigation_instability_q16(0),
      debris_collision_q16(0),
      radiation_baseline_q16(0),
      warp_cap_modifier_q16(0),
      survey_difficulty_q16(0),
      supernova_timer_ticks(0ull),
      has_supernova(false) {
}

dom_coredata_resource_modifier::dom_coredata_resource_modifier()
    : resource_id(),
      resource_id_hash(0ull),
      modifier_q16(0) {
}

dom_coredata_site_profile::dom_coredata_site_profile()
    : id(),
      id_hash(0ull),
      hazard_radiation_q16(0),
      hazard_pressure_q16(0),
      corrosion_rate_q16(0),
      temperature_extreme_q16(0),
      resource_yield(),
      access_constraints() {
}

dom_coredata_astro_body::dom_coredata_astro_body()
    : id(),
      id_hash(0ull),
      has_radius(false),
      radius_m(0ull),
      mu_mantissa(0ull),
      mu_exp10(0),
      has_rotation_rate(false),
      rotation_rate_q16(0),
      atmosphere_profile_id(),
      atmosphere_profile_id_hash(0ull) {
}

dom_coredata_state::dom_coredata_state()
    : pack_schema_version(0u),
      pack_id(),
      pack_version_num(0u),
      pack_version_str(),
      content_hash(0ull),
      pack_hash(0ull),
      sim_digest(0ull),
      anchors(),
      edges(),
      rules(),
      system_profiles(),
      site_profiles(),
      astro_bodies() {
}

int dom_coredata_load_from_bytes(const unsigned char *data,
                                 size_t size,
                                 dom_coredata_state *out_state,
                                 std::string *out_error) {
    dom::core_tlv::TlvReader r(data, size);
    dom::core_tlv::TlvRecord rec;
    std::vector<RecordView> records;
    std::vector<RecordView> content_records;
    std::string err;
    bool have_meta = false;
    bool have_rules = false;
    size_t i;

    if (!out_state || (!data && size != 0u)) {
        set_error(out_error, "invalid_argument");
        return DOM_COREDATA_INVALID_ARGUMENT;
    }

    *out_state = dom_coredata_state();
    out_state->pack_hash = dom::core_tlv::tlv_fnv1a64(data ? data : 0, size);

    while (r.next(rec)) {
        RecordView view;
        view.type_id = rec.tag;
        view.id_hash = 0ull;
        if (rec.len > 0u && rec.payload) {
            view.payload.assign(rec.payload, rec.payload + rec.len);
        }
        view.record_hash = hash_record(view.type_id, (u16)CORE_DATA_REC_VERSION_V1, view.payload);

        if (view.type_id == CORE_DATA_REC_PACK_META) {
            if (have_meta) {
                set_error(out_error, "pack_meta_duplicate");
                return DOM_COREDATA_INVALID_FORMAT;
            }
            if (!parse_pack_meta(rec.payload, rec.len, *out_state, err)) {
                set_error(out_error, err.c_str());
                return DOM_COREDATA_INVALID_FORMAT;
            }
            have_meta = true;
        } else if (view.type_id == CORE_DATA_REC_COSMO_ANCHOR) {
            dom_coredata_anchor anchor;
            if (!parse_anchor_record(view.payload, anchor, err)) {
                set_error(out_error, err.c_str());
                return DOM_COREDATA_INVALID_FORMAT;
            }
            view.id = anchor.id;
            view.id_hash = anchor.id_hash;
            out_state->anchors.push_back(anchor);
        } else if (view.type_id == CORE_DATA_REC_COSMO_EDGE) {
            dom_coredata_edge edge;
            if (!parse_edge_record(view.payload, edge, err)) {
                set_error(out_error, err.c_str());
                return DOM_COREDATA_INVALID_FORMAT;
            }
            view.id = edge.src_id + "->" + edge.dst_id;
            view.id_hash = compute_edge_key_hash(edge);
            out_state->edges.push_back(edge);
        } else if (view.type_id == CORE_DATA_REC_COSMO_RULES) {
            if (have_rules) {
                set_error(out_error, "rules_multiple");
                return DOM_COREDATA_INVALID_FORMAT;
            }
            if (!parse_rules_record(view.payload, out_state->rules, err)) {
                set_error(out_error, err.c_str());
                return DOM_COREDATA_INVALID_FORMAT;
            }
            view.id.clear();
            view.id_hash = 0ull;
            have_rules = true;
        } else if (view.type_id == CORE_DATA_REC_MECH_SYSTEM) {
            dom_coredata_system_profile prof;
            if (!parse_system_profile_record(view.payload, prof, err)) {
                set_error(out_error, err.c_str());
                return DOM_COREDATA_INVALID_FORMAT;
            }
            view.id = prof.id;
            view.id_hash = prof.id_hash;
            out_state->system_profiles.push_back(prof);
        } else if (view.type_id == CORE_DATA_REC_MECH_SITE) {
            dom_coredata_site_profile prof;
            if (!parse_site_profile_record(view.payload, prof, err)) {
                set_error(out_error, err.c_str());
                return DOM_COREDATA_INVALID_FORMAT;
            }
            view.id = prof.id;
            view.id_hash = prof.id_hash;
            out_state->site_profiles.push_back(prof);
        } else if (view.type_id == CORE_DATA_REC_ASTRO_BODY) {
            dom_coredata_astro_body body;
            if (!parse_astro_body_record(view.payload, body, err)) {
                set_error(out_error, err.c_str());
                return DOM_COREDATA_INVALID_FORMAT;
            }
            view.id = body.id;
            view.id_hash = body.id_hash;
            out_state->astro_bodies.push_back(body);
        } else {
            set_error(out_error, "record_unknown_type");
            return DOM_COREDATA_INVALID_FORMAT;
        }

        records.push_back(view);
        if (view.type_id != CORE_DATA_REC_PACK_META) {
            content_records.push_back(view);
        }
    }

    if (r.remaining() != 0u) {
        set_error(out_error, "pack_truncated");
        return DOM_COREDATA_INVALID_FORMAT;
    }
    if (!have_meta) {
        set_error(out_error, "pack_meta_missing");
        return DOM_COREDATA_MISSING_REQUIRED;
    }
    if (out_state->anchors.empty() || out_state->system_profiles.empty() ||
        out_state->site_profiles.empty() || out_state->astro_bodies.empty() ||
        !out_state->rules.present) {
        set_error(out_error, "required_records_missing");
        return DOM_COREDATA_MISSING_REQUIRED;
    }
    if (!record_is_canonical(records)) {
        set_error(out_error, "record_order_invalid");
        return DOM_COREDATA_INVALID_FORMAT;
    }

    std::sort(content_records.begin(), content_records.end(), record_less);
    if (out_state->content_hash != hash_content(content_records)) {
        set_error(out_error, "content_hash_mismatch");
        return DOM_COREDATA_INVALID_FORMAT;
    }

    for (i = 0u; i < content_records.size(); ++i) {
        if (i > 0u && record_less(content_records[i], content_records[i - 1u])) {
            set_error(out_error, "content_record_order_invalid");
            return DOM_COREDATA_INVALID_FORMAT;
        }
        if (i > 0u && content_records[i].type_id == content_records[i - 1u].type_id &&
            content_records[i].id_hash == content_records[i - 1u].id_hash &&
            content_records[i].id == content_records[i - 1u].id) {
            set_error(out_error, "duplicate_record_id");
            return DOM_COREDATA_DUPLICATE_ID;
        }
    }

    {
        std::vector<u64> mech_profile_hashes;
        for (i = 0u; i < out_state->system_profiles.size(); ++i) {
            mech_profile_hashes.push_back(out_state->system_profiles[i].id_hash);
        }
        for (i = 0u; i < out_state->anchors.size(); ++i) {
            bool found = false;
            size_t j;
            for (j = 0u; j < mech_profile_hashes.size(); ++j) {
                if (mech_profile_hashes[j] == out_state->anchors[i].mechanics_profile_id_hash) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                set_error(out_error, "anchor_mechanics_profile_missing");
                return DOM_COREDATA_MISSING_REFERENCE;
            }
        }
    }

    {
        std::vector<u64> anchor_ids;
        anchor_ids.reserve(out_state->anchors.size());
        for (i = 0u; i < out_state->anchors.size(); ++i) {
            anchor_ids.push_back(out_state->anchors[i].id_hash);
        }
        for (i = 0u; i < out_state->edges.size(); ++i) {
            bool src_ok = false;
            bool dst_ok = false;
            size_t j;
            for (j = 0u; j < anchor_ids.size(); ++j) {
                if (anchor_ids[j] == out_state->edges[i].src_id_hash) {
                    src_ok = true;
                }
                if (anchor_ids[j] == out_state->edges[i].dst_id_hash) {
                    dst_ok = true;
                }
                if (src_ok && dst_ok) {
                    break;
                }
            }
            if (!src_ok || !dst_ok) {
                set_error(out_error, "edge_missing_anchor");
                return DOM_COREDATA_MISSING_REFERENCE;
            }
        }
    }

    if (out_state->rules.present) {
        apply_rules_sorted(out_state->rules.cluster_density);
        apply_rules_sorted(out_state->rules.metallicity_bias);
        apply_rules_sorted(out_state->rules.hazard_frequency);
    }

    out_state->sim_digest = compute_sim_digest(*out_state);
    return DOM_COREDATA_OK;
}

int dom_coredata_load_from_file(const char *path,
                                dom_coredata_state *out_state,
                                std::string *out_error) {
    std::vector<unsigned char> bytes;
    std::string err;
    if (!out_state) {
        set_error(out_error, "invalid_argument");
        return DOM_COREDATA_INVALID_ARGUMENT;
    }
    if (!read_file_bytes(path, bytes, err)) {
        set_error(out_error, err.c_str());
        return DOM_COREDATA_IO_ERROR;
    }
    return dom_coredata_load_from_bytes(bytes.empty() ? 0 : &bytes[0],
                                        bytes.size(),
                                        out_state,
                                        out_error);
}

u64 dom_coredata_compute_sim_digest(const dom_coredata_state *state) {
    if (!state) {
        return 0ull;
    }
    return compute_sim_digest(*state);
}

int dom_coredata_apply_to_registries(const dom_coredata_state *state,
                                     dom::dom_cosmo_graph *graph,
                                     dom_mech_profiles *mech_profiles,
                                     dom_system_registry *systems,
                                     dom_body_registry *bodies,
                                     u32 ups,
                                     std::string *out_error) {
    dom::dom_cosmo_graph temp;
    dom::dom_cosmo_graph_config cfg;
    dom::dom_cosmo_edge_params edge_params;
    dom_system_desc sys_desc;
    dom_body_desc body_desc;
    dom_mech_system_profile_desc mech_sys_desc;
    dom_mech_site_profile_desc mech_site_desc;
    u64 filament_id = 0ull;
    u64 cluster_id = 0ull;
    u64 galaxy_id = 0ull;
    u64 sol_system_id = 0ull;
    size_t i;

    if (!state || !graph || !mech_profiles || !systems || !bodies) {
        set_error(out_error, "invalid_argument");
        return DOM_COREDATA_INVALID_ARGUMENT;
    }

    cfg = graph->config;
    if (dom::dom_cosmo_graph_init(&temp, graph->seed, &cfg) != dom::DOM_COSMO_GRAPH_OK) {
        set_error(out_error, "cosmo_graph_init_failed");
        return DOM_COREDATA_ERR;
    }

    if (dom_id_hash64("milky_way_filament", 19u, &filament_id) != DOM_SPACETIME_OK ||
        dom_id_hash64("milky_way_cluster", 18u, &cluster_id) != DOM_SPACETIME_OK ||
        dom_id_hash64("milky_way", 9u, &galaxy_id) != DOM_SPACETIME_OK) {
        set_error(out_error, "core_id_hash_failed");
        return DOM_COREDATA_ERR;
    }

    if (dom::dom_cosmo_graph_add_entity(&temp,
                                        dom::DOM_COSMO_KIND_FILAMENT,
                                        "milky_way_filament",
                                        0ull,
                                        0) != dom::DOM_COSMO_GRAPH_OK) {
        set_error(out_error, "cosmo_filament_add_failed");
        return DOM_COREDATA_ERR;
    }
    if (dom::dom_cosmo_graph_add_entity(&temp,
                                        dom::DOM_COSMO_KIND_CLUSTER,
                                        "milky_way_cluster",
                                        filament_id,
                                        0) != dom::DOM_COSMO_GRAPH_OK) {
        set_error(out_error, "cosmo_cluster_add_failed");
        return DOM_COREDATA_ERR;
    }
    if (dom::dom_cosmo_graph_add_entity(&temp,
                                        dom::DOM_COSMO_KIND_GALAXY,
                                        "milky_way",
                                        cluster_id,
                                        0) != dom::DOM_COSMO_GRAPH_OK) {
        set_error(out_error, "cosmo_galaxy_add_failed");
        return DOM_COREDATA_ERR;
    }

    for (i = 0u; i < state->anchors.size(); ++i) {
        const dom_coredata_anchor &anchor = state->anchors[i];
        u32 kind = 0u;
        u64 parent_id = 0ull;
        if (anchor.kind == CORE_DATA_KIND_REGION) {
            kind = dom::DOM_COSMO_KIND_CLUSTER;
            parent_id = filament_id;
        } else if (anchor.kind == CORE_DATA_KIND_SYSTEM) {
            kind = dom::DOM_COSMO_KIND_SYSTEM;
            parent_id = galaxy_id;
        } else {
            set_error(out_error, "anchor_kind_invalid");
            return DOM_COREDATA_INVALID_FORMAT;
        }
        if (dom::dom_cosmo_graph_add_entity(&temp,
                                            kind,
                                            anchor.id.c_str(),
                                            parent_id,
                                            0) != dom::DOM_COSMO_GRAPH_OK) {
            set_error(out_error, "cosmo_anchor_add_failed");
            return DOM_COREDATA_ERR;
        }
    }

    for (i = 0u; i < state->edges.size(); ++i) {
        const dom_coredata_edge &edge = state->edges[i];
        edge_params.duration_ticks = edge.duration_ticks;
        edge_params.cost = (u32)(edge.cost_profile_id_hash & 0xffffffffu);
        edge_params.event_table_id = edge.has_hazard ? edge.hazard_profile_id_hash : 0ull;
        if (dom::dom_cosmo_graph_add_travel_edge(&temp,
                                                 edge.src_id_hash,
                                                 edge.dst_id_hash,
                                                 &edge_params,
                                                 0) != dom::DOM_COSMO_GRAPH_OK) {
            set_error(out_error, "cosmo_edge_add_failed");
            return DOM_COREDATA_ERR;
        }
    }

    if (dom::dom_cosmo_graph_validate(&temp, 0) != dom::DOM_COSMO_GRAPH_OK) {
        set_error(out_error, "cosmo_graph_validate_failed");
        return DOM_COREDATA_ERR;
    }
    *graph = temp;

    for (i = 0u; i < state->system_profiles.size(); ++i) {
        const dom_coredata_system_profile &p = state->system_profiles[i];
        mech_sys_desc.id = p.id.c_str();
        mech_sys_desc.id_len = (u32)p.id.size();
        mech_sys_desc.id_hash = p.id_hash;
        mech_sys_desc.navigation_instability_q16 = p.navigation_instability_q16;
        mech_sys_desc.debris_collision_q16 = p.debris_collision_q16;
        mech_sys_desc.radiation_baseline_q16 = p.radiation_baseline_q16;
        mech_sys_desc.warp_cap_modifier_q16 = p.warp_cap_modifier_q16;
        mech_sys_desc.survey_difficulty_q16 = p.survey_difficulty_q16;
        mech_sys_desc.supernova_timer_ticks = p.supernova_timer_ticks;
        mech_sys_desc.has_supernova_timer = p.has_supernova ? 1u : 0u;
        if (dom_mech_profiles_register_system(mech_profiles, &mech_sys_desc) != DOM_MECH_PROFILES_OK) {
            set_error(out_error, "mech_system_register_failed");
            return DOM_COREDATA_ERR;
        }
    }

    for (i = 0u; i < state->site_profiles.size(); ++i) {
        const dom_coredata_site_profile &p = state->site_profiles[i];
        mech_site_desc.id = p.id.c_str();
        mech_site_desc.id_len = (u32)p.id.size();
        mech_site_desc.id_hash = p.id_hash;
        mech_site_desc.hazard_radiation_q16 = p.hazard_radiation_q16;
        mech_site_desc.hazard_pressure_q16 = p.hazard_pressure_q16;
        mech_site_desc.corrosion_rate_q16 = p.corrosion_rate_q16;
        mech_site_desc.temperature_extreme_q16 = p.temperature_extreme_q16;
        if (dom_mech_profiles_register_site(mech_profiles, &mech_site_desc) != DOM_MECH_PROFILES_OK) {
            set_error(out_error, "mech_site_register_failed");
            return DOM_COREDATA_ERR;
        }
    }

    if (dom_id_hash64("sol", 3u, &sol_system_id) != DOM_SPACETIME_OK) {
        set_error(out_error, "system_hash_failed");
        return DOM_COREDATA_ERR;
    }

    for (i = 0u; i < state->anchors.size(); ++i) {
        const dom_coredata_anchor &anchor = state->anchors[i];
        if (anchor.kind != CORE_DATA_KIND_SYSTEM) {
            continue;
        }
        sys_desc.string_id = anchor.id.c_str();
        sys_desc.string_id_len = (u32)anchor.id.size();
        sys_desc.id = anchor.id_hash;
        sys_desc.parent_id = galaxy_id;
        if (dom_system_registry_register(systems, &sys_desc) != DOM_SYSTEM_REGISTRY_OK) {
            set_error(out_error, "system_register_failed");
            return DOM_COREDATA_ERR;
        }
    }

    for (i = 0u; i < state->astro_bodies.size(); ++i) {
        const dom_coredata_astro_body &body = state->astro_bodies[i];
        u64 mu_m3_s2 = 0ull;
        u64 rotation_ticks = 0ull;
        u32 kind = DOM_BODY_KIND_PLANET;
        if (!body.has_radius) {
            continue;
        }
        if (!compute_mu_m3_s2(body, mu_m3_s2)) {
            set_error(out_error, "astro_mu_invalid");
            return DOM_COREDATA_INVALID_FORMAT;
        }
        if (body.id == "sol") {
            kind = DOM_BODY_KIND_STAR;
        } else if (body.id == "earth") {
            kind = DOM_BODY_KIND_PLANET;
        }
        if (body.has_rotation_rate) {
            (void)compute_rotation_ticks(body.rotation_rate_q16, ups, rotation_ticks);
        }
        body_desc.string_id = body.id.c_str();
        body_desc.string_id_len = (u32)body.id.size();
        body_desc.id = body.id_hash;
        body_desc.system_id = sol_system_id;
        body_desc.kind = kind;
        body_desc.radius_m = (q48_16)body.radius_m;
        body_desc.mu_m3_s2 = mu_m3_s2;
        body_desc.rotation_period_ticks = rotation_ticks;
        body_desc.rotation_epoch_tick = 0ull;
        body_desc.axial_tilt_turns = 0;
        body_desc.has_axial_tilt = 0u;
        if (dom_body_registry_register(bodies, &body_desc) != DOM_BODY_REGISTRY_OK) {
            set_error(out_error, "body_register_failed");
            return DOM_COREDATA_ERR;
        }
    }

    return DOM_COREDATA_OK;
}
