/*
FILE: source/dominium/tools/coredata_compile/coredata_emit_tlv.cpp
MODULE: Dominium
PURPOSE: Coredata compiler TLV emission (deterministic pack bytes).
*/
#include "coredata_emit_tlv.h"

#include <algorithm>
#include <cstdio>
#include <cstring>

#include "coredata_schema.h"
#include "dominium/core_tlv.h"

extern "C" {
#include "domino/core/spacetime.h"
}

namespace dom {
namespace tools {

CoredataRecord::CoredataRecord()
    : type_id(0u),
      version(0u),
      id(),
      id_hash(0ull),
      payload(),
      record_hash(0ull) {
}

CoredataPack::CoredataPack()
    : pack_id(),
      pack_version_str(),
      pack_version_num(0u),
      pack_schema_version(0u),
      content_hash(0ull),
      pack_hash(0ull),
      records(),
      pack_bytes() {
}

CoredataEmitOptions::CoredataEmitOptions()
    : pack_id(),
      pack_version_str(),
      pack_version_num(0u),
      pack_schema_version(0u) {
}

namespace {

static void add_error(std::vector<CoredataError> &errors,
                      const char *code,
                      const std::string &message) {
    CoredataError e;
    e.path = "emit";
    e.line = 0;
    e.code = code ? code : "error";
    e.message = message;
    errors.push_back(e);
}

static bool map_kind(const std::string &s, u32 &out) {
    if (s == "system") {
        out = CORE_DATA_KIND_SYSTEM;
        return true;
    }
    if (s == "region") {
        out = CORE_DATA_KIND_REGION;
        return true;
    }
    return false;
}

static bool map_system_class(const std::string &s, u32 &out) {
    if (s == "single") {
        out = CORE_DATA_SYSTEM_SINGLE;
        return true;
    }
    if (s == "binary") {
        out = CORE_DATA_SYSTEM_BINARY;
        return true;
    }
    if (s == "cluster") {
        out = CORE_DATA_SYSTEM_CLUSTER;
        return true;
    }
    if (s == "remnant") {
        out = CORE_DATA_SYSTEM_REMNANT;
        return true;
    }
    if (s == "exotic") {
        out = CORE_DATA_SYSTEM_EXOTIC;
        return true;
    }
    return false;
}

static bool map_region_type(const std::string &s, u32 &out) {
    if (s == "nebula") {
        out = CORE_DATA_REGION_NEBULA;
        return true;
    }
    if (s == "open_cluster") {
        out = CORE_DATA_REGION_OPEN_CLUSTER;
        return true;
    }
    if (s == "globular_cluster") {
        out = CORE_DATA_REGION_GLOBULAR_CLUSTER;
        return true;
    }
    if (s == "galactic_core") {
        out = CORE_DATA_REGION_GALACTIC_CORE;
        return true;
    }
    return false;
}

static bool map_evidence(const std::string &s, u32 &out) {
    if (s == "confirmed") {
        out = CORE_DATA_EVIDENCE_CONFIRMED;
        return true;
    }
    if (s == "candidate") {
        out = CORE_DATA_EVIDENCE_CANDIDATE;
        return true;
    }
    if (s == "historical") {
        out = CORE_DATA_EVIDENCE_HISTORICAL;
        return true;
    }
    if (s == "fictionalized") {
        out = CORE_DATA_EVIDENCE_FICTIONALIZED;
        return true;
    }
    return false;
}

static bool id_hash64(const std::string &id, u64 &out_hash) {
    if (id.empty()) {
        out_hash = 0ull;
        return true;
    }
    return dom_id_hash64(id.c_str(), (u32)id.size(), &out_hash) == DOM_SPACETIME_OK;
}

static void write_i32_le(unsigned char out[4], i32 v) {
    dom::core_tlv::tlv_write_u32_le(out, (u32)v);
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

static u64 hash_content(const std::vector<CoredataRecord> &records) {
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

static bool record_less(const CoredataRecord &a, const CoredataRecord &b) {
    if (a.type_id != b.type_id) {
        return a.type_id < b.type_id;
    }
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static std::vector<std::string> sorted_strings(const std::vector<std::string> &in) {
    std::vector<std::string> out = in;
    std::sort(out.begin(), out.end());
    return out;
}

static bool rules_entry_less(const CoredataRulesEntry &a, const CoredataRulesEntry &b) {
    return a.region_type < b.region_type;
}

static bool resource_mod_less(const CoredataResourceModifier &a, const CoredataResourceModifier &b) {
    return a.resource_id < b.resource_id;
}

static std::vector<CoredataRulesEntry> sorted_rules(const std::vector<CoredataRulesEntry> &in) {
    std::vector<CoredataRulesEntry> out = in;
    std::sort(out.begin(), out.end(), rules_entry_less);
    return out;
}

static std::vector<CoredataResourceModifier> sorted_resources(const std::vector<CoredataResourceModifier> &in) {
    std::vector<CoredataResourceModifier> out = in;
    std::sort(out.begin(), out.end(), resource_mod_less);
    return out;
}

static bool emit_anchor(const CoredataAnchor &a,
                        CoredataRecord &out,
                        std::vector<CoredataError> &errors) {
    u64 id_hash = 0ull;
    u32 kind = 0u;
    u32 system_class = 0u;
    u32 region_type = 0u;
    u32 evidence = 0u;
    dom::core_tlv::TlvWriter w;

    if (!id_hash64(a.id, id_hash)) {
        add_error(errors, "anchor_id_hash_failed", a.id);
        return false;
    }
    if (!map_kind(a.kind, kind)) {
        add_error(errors, "anchor_kind_invalid", a.id);
        return false;
    }
    if (!map_evidence(a.evidence_grade, evidence)) {
        add_error(errors, "anchor_evidence_invalid", a.id);
        return false;
    }

    w.add_string(CORE_DATA_ANCHOR_TAG_ID, a.id);
    w.add_u64(CORE_DATA_ANCHOR_TAG_ID_HASH, id_hash);
    w.add_u32(CORE_DATA_ANCHOR_TAG_KIND, kind);
    if (!a.display_name.empty()) {
        w.add_string(CORE_DATA_ANCHOR_TAG_DISPLAY_NAME, a.display_name);
    }
    if (kind == CORE_DATA_KIND_SYSTEM) {
        if (!map_system_class(a.system_class, system_class)) {
            add_error(errors, "anchor_system_class_invalid", a.id);
            return false;
        }
        w.add_u32(CORE_DATA_ANCHOR_TAG_SYSTEM_CLASS, system_class);
    } else if (kind == CORE_DATA_KIND_REGION) {
        if (!map_region_type(a.region_type, region_type)) {
            add_error(errors, "anchor_region_type_invalid", a.id);
            return false;
        }
        w.add_u32(CORE_DATA_ANCHOR_TAG_REGION_TYPE, region_type);
    }
    w.add_u32(CORE_DATA_ANCHOR_TAG_EVIDENCE_GRADE, evidence);
    w.add_string(CORE_DATA_ANCHOR_TAG_MECH_PROFILE_ID, a.mechanics_profile_id);
    w.add_u32(CORE_DATA_ANCHOR_TAG_ANCHOR_WEIGHT, a.anchor_weight);

    if (!a.tags.empty()) {
        std::vector<std::string> tags = sorted_strings(a.tags);
        size_t i;
        for (i = 0u; i < tags.size(); ++i) {
            if (!tags[i].empty()) {
                w.add_string(CORE_DATA_ANCHOR_TAG_TAG, tags[i]);
            }
        }
    }

    if (a.has_present_pos) {
        unsigned char buf[12];
        write_i32_le(buf, a.present_pos_q16[0]);
        write_i32_le(buf + 4u, a.present_pos_q16[1]);
        write_i32_le(buf + 8u, a.present_pos_q16[2]);
        w.add_bytes(CORE_DATA_ANCHOR_TAG_PRESENTATION_POS, buf, 12u);
    }

    out.type_id = CORE_DATA_REC_COSMO_ANCHOR;
    out.version = (u16)CORE_DATA_REC_VERSION_V1;
    out.id = a.id;
    out.id_hash = id_hash;
    out.payload = w.bytes();
    out.record_hash = hash_record(out.type_id, out.version, out.payload);
    return true;
}

static bool emit_rules(const CoredataProceduralRules &r,
                       CoredataRecord &out,
                       std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvWriter w;
    size_t i;

    if (!r.present) {
        return false;
    }

    w.add_u32(CORE_DATA_RULES_TAG_SYS_MIN, r.systems_per_anchor_min);
    w.add_u32(CORE_DATA_RULES_TAG_SYS_MAX, r.systems_per_anchor_max);
    w.add_i32(CORE_DATA_RULES_TAG_RED_DWARF_RATIO, r.red_dwarf_ratio_q16);
    w.add_i32(CORE_DATA_RULES_TAG_BINARY_RATIO, r.binary_ratio_q16);
    w.add_i32(CORE_DATA_RULES_TAG_EXOTIC_RATIO, r.exotic_ratio_q16);

    {
        std::vector<CoredataRulesEntry> entries = sorted_rules(r.cluster_density);
        for (i = 0u; i < entries.size(); ++i) {
            u32 region = 0u;
            dom::core_tlv::TlvWriter inner;
            if (!map_region_type(entries[i].region_type, region)) {
                add_error(errors, "rules_region_type_invalid", entries[i].region_type);
                return false;
            }
            inner.add_u32(CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE, region);
            inner.add_i32(CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16, entries[i].value_q16);
            w.add_container(CORE_DATA_RULES_TAG_CLUSTER_DENSITY, inner.bytes());
        }
    }
    {
        std::vector<CoredataRulesEntry> entries = sorted_rules(r.metallicity_bias);
        for (i = 0u; i < entries.size(); ++i) {
            u32 region = 0u;
            dom::core_tlv::TlvWriter inner;
            if (!map_region_type(entries[i].region_type, region)) {
                add_error(errors, "rules_region_type_invalid", entries[i].region_type);
                return false;
            }
            inner.add_u32(CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE, region);
            inner.add_i32(CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16, entries[i].value_q16);
            w.add_container(CORE_DATA_RULES_TAG_METALLICITY_BIAS, inner.bytes());
        }
    }
    {
        std::vector<CoredataRulesEntry> entries = sorted_rules(r.hazard_frequency);
        for (i = 0u; i < entries.size(); ++i) {
            u32 region = 0u;
            dom::core_tlv::TlvWriter inner;
            if (!map_region_type(entries[i].region_type, region)) {
                add_error(errors, "rules_region_type_invalid", entries[i].region_type);
                return false;
            }
            inner.add_u32(CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE, region);
            inner.add_i32(CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16, entries[i].value_q16);
            w.add_container(CORE_DATA_RULES_TAG_HAZARD_FREQUENCY, inner.bytes());
        }
    }

    out.type_id = CORE_DATA_REC_COSMO_RULES;
    out.version = (u16)CORE_DATA_REC_VERSION_V1;
    out.id = "";
    out.id_hash = 0ull;
    out.payload = w.bytes();
    out.record_hash = hash_record(out.type_id, out.version, out.payload);
    return true;
}

static bool emit_system_profile(const CoredataSystemProfile &p,
                                CoredataRecord &out,
                                std::vector<CoredataError> &errors) {
    u64 id_hash = 0ull;
    dom::core_tlv::TlvWriter w;

    if (!id_hash64(p.id, id_hash)) {
        add_error(errors, "system_profile_id_hash_failed", p.id);
        return false;
    }

    w.add_string(CORE_DATA_MECH_SYS_TAG_ID, p.id);
    w.add_u64(CORE_DATA_MECH_SYS_TAG_ID_HASH, id_hash);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_NAV_INSTABILITY, p.navigation_instability_q16);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_DEBRIS_COLLISION, p.debris_collision_q16);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_RADIATION_BASELINE, p.radiation_baseline_q16);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_WARP_CAP, p.warp_cap_q16);
    w.add_i32(CORE_DATA_MECH_SYS_TAG_SURVEY_DIFFICULTY, p.survey_difficulty_q16);
    if (p.has_supernova_ticks) {
        w.add_u64(CORE_DATA_MECH_SYS_TAG_SUPERNOVA_TICKS, p.supernova_timer_ticks);
    }

    out.type_id = CORE_DATA_REC_MECH_SYSTEM;
    out.version = (u16)CORE_DATA_REC_VERSION_V1;
    out.id = p.id;
    out.id_hash = id_hash;
    out.payload = w.bytes();
    out.record_hash = hash_record(out.type_id, out.version, out.payload);
    return true;
}

static bool emit_site_profile(const CoredataSiteProfile &p,
                              CoredataRecord &out,
                              std::vector<CoredataError> &errors) {
    u64 id_hash = 0ull;
    dom::core_tlv::TlvWriter w;
    size_t i;

    if (!id_hash64(p.id, id_hash)) {
        add_error(errors, "site_profile_id_hash_failed", p.id);
        return false;
    }

    w.add_string(CORE_DATA_MECH_SITE_TAG_ID, p.id);
    w.add_u64(CORE_DATA_MECH_SITE_TAG_ID_HASH, id_hash);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_HAZARD_RAD, p.hazard_radiation_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_HAZARD_PRESS, p.hazard_pressure_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_CORROSION_RATE, p.corrosion_rate_q16);
    w.add_i32(CORE_DATA_MECH_SITE_TAG_TEMP_EXTREME, p.temperature_extreme_q16);

    if (!p.resource_yield.empty()) {
        std::vector<CoredataResourceModifier> mods = sorted_resources(p.resource_yield);
        for (i = 0u; i < mods.size(); ++i) {
            dom::core_tlv::TlvWriter inner;
            inner.add_string(CORE_DATA_MECH_SITE_RES_TAG_ID, mods[i].resource_id);
            inner.add_i32(CORE_DATA_MECH_SITE_RES_TAG_MOD_Q16, mods[i].modifier_q16);
            w.add_container(CORE_DATA_MECH_SITE_TAG_RESOURCE_YIELD, inner.bytes());
        }
    }

    if (!p.access_constraints.empty()) {
        std::vector<std::string> access = sorted_strings(p.access_constraints);
        for (i = 0u; i < access.size(); ++i) {
            if (!access[i].empty()) {
                w.add_string(CORE_DATA_MECH_SITE_TAG_ACCESS_CONSTRAINT, access[i]);
            }
        }
    }

    out.type_id = CORE_DATA_REC_MECH_SITE;
    out.version = (u16)CORE_DATA_REC_VERSION_V1;
    out.id = p.id;
    out.id_hash = id_hash;
    out.payload = w.bytes();
    out.record_hash = hash_record(out.type_id, out.version, out.payload);
    return true;
}

static bool emit_astro_body(const CoredataAstroBody &b,
                            CoredataRecord &out,
                            std::vector<CoredataError> &errors) {
    u64 id_hash = 0ull;
    dom::core_tlv::TlvWriter w;

    if (!id_hash64(b.id, id_hash)) {
        add_error(errors, "astro_id_hash_failed", b.id);
        return false;
    }

    w.add_string(CORE_DATA_ASTRO_TAG_ID, b.id);
    w.add_u64(CORE_DATA_ASTRO_TAG_ID_HASH, id_hash);
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

    out.type_id = CORE_DATA_REC_ASTRO_BODY;
    out.version = (u16)CORE_DATA_REC_VERSION_V1;
    out.id = b.id;
    out.id_hash = id_hash;
    out.payload = w.bytes();
    out.record_hash = hash_record(out.type_id, out.version, out.payload);
    return true;
}

static void emit_pack_meta(const CoredataEmitOptions &opts,
                           u64 content_hash,
                           CoredataRecord &out) {
    dom::core_tlv::TlvWriter w;

    w.add_u32(CORE_DATA_META_TAG_PACK_SCHEMA_VERSION, opts.pack_schema_version);
    w.add_string(CORE_DATA_META_TAG_PACK_ID, opts.pack_id);
    w.add_u32(CORE_DATA_META_TAG_PACK_VERSION_NUM, opts.pack_version_num);
    if (!opts.pack_version_str.empty()) {
        w.add_string(CORE_DATA_META_TAG_PACK_VERSION_STR, opts.pack_version_str);
    }
    w.add_u64(CORE_DATA_META_TAG_CONTENT_HASH, content_hash);

    out.type_id = CORE_DATA_REC_PACK_META;
    out.version = (u16)CORE_DATA_REC_VERSION_V1;
    out.id = "";
    out.id_hash = 0ull;
    out.payload = w.bytes();
    out.record_hash = hash_record(out.type_id, out.version, out.payload);
}

} // namespace

bool coredata_emit_pack(const CoredataData &data,
                        const CoredataEmitOptions &opts,
                        CoredataPack &out_pack,
                        std::vector<CoredataError> &errors) {
    std::vector<CoredataRecord> records;
    CoredataRecord rec;
    size_t i;

    errors.clear();
    out_pack = CoredataPack();

    if (opts.pack_id.empty()) {
        add_error(errors, "pack_id_missing", "pack_id");
        return false;
    }

    for (i = 0u; i < data.anchors.size(); ++i) {
        rec = CoredataRecord();
        if (!emit_anchor(data.anchors[i], rec, errors)) {
            return false;
        }
        records.push_back(rec);
    }

    if (!data.rules.empty()) {
        rec = CoredataRecord();
        if (!emit_rules(data.rules[0], rec, errors)) {
            return false;
        }
        records.push_back(rec);
    }

    for (i = 0u; i < data.system_profiles.size(); ++i) {
        rec = CoredataRecord();
        if (!emit_system_profile(data.system_profiles[i], rec, errors)) {
            return false;
        }
        records.push_back(rec);
    }

    for (i = 0u; i < data.site_profiles.size(); ++i) {
        rec = CoredataRecord();
        if (!emit_site_profile(data.site_profiles[i], rec, errors)) {
            return false;
        }
        records.push_back(rec);
    }

    for (i = 0u; i < data.astro_bodies.size(); ++i) {
        rec = CoredataRecord();
        if (!emit_astro_body(data.astro_bodies[i], rec, errors)) {
            return false;
        }
        records.push_back(rec);
    }

    std::sort(records.begin(), records.end(), record_less);
    out_pack.content_hash = hash_content(records);

    rec = CoredataRecord();
    emit_pack_meta(opts, out_pack.content_hash, rec);
    records.push_back(rec);
    std::sort(records.begin(), records.end(), record_less);

    {
        dom::core_tlv::TlvWriter pack_writer;
        for (i = 0u; i < records.size(); ++i) {
            pack_writer.add_bytes(records[i].type_id,
                                  records[i].payload.empty() ? 0 : &records[i].payload[0],
                                  (u32)records[i].payload.size());
        }
        out_pack.pack_bytes = pack_writer.bytes();
        out_pack.pack_hash = dom::core_tlv::tlv_fnv1a64(out_pack.pack_bytes.empty() ? 0 : &out_pack.pack_bytes[0],
                                                        out_pack.pack_bytes.size());
    }

    out_pack.pack_id = opts.pack_id;
    out_pack.pack_version_str = opts.pack_version_str;
    out_pack.pack_version_num = opts.pack_version_num;
    out_pack.pack_schema_version = opts.pack_schema_version;
    out_pack.records = records;

    return errors.empty();
}

} // namespace tools
} // namespace dom
