/*
FILE: source/dominium/tools/coredata_validate/coredata_validate_load.cpp
MODULE: Dominium
PURPOSE: Coredata validator loaders (authoring + pack/manifest).
*/
#include "coredata_validate_load.h"

#include <cstdio>
#include <cstring>

#include "coredata_compile/coredata_manifest.h"
#include "coredata_compile/coredata_schema.h"
#include "dominium/core_tlv.h"

extern "C" {
#include "domino/core/spacetime.h"
}

namespace dom {
namespace tools {

CoredataPackRecordView::CoredataPackRecordView()
    : type_id(0u),
      id(),
      id_hash(0ull),
      payload(),
      record_hash(0ull) {
}

CoredataPackView::CoredataPackView()
    : has_pack_meta(false),
      pack_schema_version(0u),
      pack_id(),
      pack_version_num(0u),
      pack_version_str(),
      content_hash(0ull),
      pack_hash(0ull),
      records() {
}

CoredataManifestRecordView::CoredataManifestRecordView()
    : type_id(0u),
      version(0u),
      id(),
      id_hash(0ull),
      record_hash(0ull) {
}

CoredataManifestView::CoredataManifestView()
    : present(false),
      schema_version(0u),
      pack_id(),
      pack_version_num(0u),
      pack_version_str(),
      pack_schema_version(0u),
      content_hash(0ull),
      pack_hash(0ull),
      records() {
}

namespace {

static void add_error(std::vector<CoredataError> &errors,
                      const std::string &path,
                      const char *code,
                      const std::string &message) {
    CoredataError e;
    e.path = path;
    e.line = 0;
    e.code = code ? code : "error";
    e.message = message;
    errors.push_back(e);
}

static bool read_file_bytes(const std::string &path,
                            std::vector<unsigned char> &out,
                            std::string &err) {
    std::FILE *f = std::fopen(path.c_str(), "rb");
    long size = 0;
    size_t read = 0u;
    if (!f) {
        err = "open_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        err = "seek_failed";
        return false;
    }
    size = std::ftell(f);
    if (size < 0) {
        std::fclose(f);
        err = "tell_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        err = "seek_failed";
        return false;
    }
    out.assign((size_t)size, 0u);
    if (size > 0) {
        read = std::fread(&out[0], 1u, (size_t)size, f);
        if (read != (size_t)size) {
            std::fclose(f);
            err = "read_failed";
            return false;
        }
    }
    std::fclose(f);
    return true;
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

static bool parse_u32_field(const std::string &path,
                            u32 tag,
                            const dom::core_tlv::TlvRecord &rec,
                            u32 &out,
                            std::vector<CoredataError> &errors) {
    if (!dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out)) {
        char buf[64];
        std::sprintf(buf, "u32 tag %u invalid", tag);
        add_error(errors, path, "field_invalid", buf);
        return false;
    }
    return true;
}

static bool parse_u64_field(const std::string &path,
                            u32 tag,
                            const dom::core_tlv::TlvRecord &rec,
                            u64 &out,
                            std::vector<CoredataError> &errors) {
    if (!dom::core_tlv::tlv_read_u64_le(rec.payload, rec.len, out)) {
        char buf[64];
        std::sprintf(buf, "u64 tag %u invalid", tag);
        add_error(errors, path, "field_invalid", buf);
        return false;
    }
    return true;
}

static bool parse_i32_field(const std::string &path,
                            u32 tag,
                            const dom::core_tlv::TlvRecord &rec,
                            i32 &out,
                            std::vector<CoredataError> &errors) {
    if (!dom::core_tlv::tlv_read_i32_le(rec.payload, rec.len, out)) {
        char buf[64];
        std::sprintf(buf, "i32 tag %u invalid", tag);
        add_error(errors, path, "field_invalid", buf);
        return false;
    }
    return true;
}

static std::string parse_string_field(const dom::core_tlv::TlvRecord &rec) {
    return dom::core_tlv::tlv_read_string(rec.payload, rec.len);
}

static bool parse_pack_meta(const std::string &path,
                            const unsigned char *data,
                            u32 len,
                            CoredataPackView &out,
                            std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvReader r(data, len);
    dom::core_tlv::TlvRecord rec;
    bool has_schema = false;
    bool has_pack_id = false;
    bool has_version_num = false;
    bool has_content_hash = false;

    while (r.next(rec)) {
        switch (rec.tag) {
            case CORE_DATA_META_TAG_PACK_SCHEMA_VERSION:
                if (has_schema) {
                    add_error(errors, path, "pack_meta_duplicate_field", "pack_schema_version");
                    break;
                }
                if (parse_u32_field(path, rec.tag, rec, out.pack_schema_version, errors)) {
                    has_schema = true;
                }
                break;
            case CORE_DATA_META_TAG_PACK_ID:
                if (has_pack_id) {
                    add_error(errors, path, "pack_meta_duplicate_field", "pack_id");
                    break;
                }
                out.pack_id = parse_string_field(rec);
                has_pack_id = true;
                break;
            case CORE_DATA_META_TAG_PACK_VERSION_NUM:
                if (has_version_num) {
                    add_error(errors, path, "pack_meta_duplicate_field", "pack_version_num");
                    break;
                }
                if (parse_u32_field(path, rec.tag, rec, out.pack_version_num, errors)) {
                    has_version_num = true;
                }
                break;
            case CORE_DATA_META_TAG_PACK_VERSION_STR:
                out.pack_version_str = parse_string_field(rec);
                break;
            case CORE_DATA_META_TAG_CONTENT_HASH:
                if (has_content_hash) {
                    add_error(errors, path, "pack_meta_duplicate_field", "content_hash");
                    break;
                }
                if (parse_u64_field(path, rec.tag, rec, out.content_hash, errors)) {
                    has_content_hash = true;
                }
                break;
            default:
                add_error(errors, path, "pack_meta_unknown_tag", "unknown tag");
                break;
        }
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "pack_meta_truncated", "pack meta TLV truncated");
    }
    if (!has_schema) {
        add_error(errors, path, "pack_meta_missing_field", "pack_schema_version");
    }
    if (!has_pack_id) {
        add_error(errors, path, "pack_meta_missing_field", "pack_id");
    }
    if (!has_version_num) {
        add_error(errors, path, "pack_meta_missing_field", "pack_version_num");
    }
    if (!has_content_hash) {
        add_error(errors, path, "pack_meta_missing_field", "content_hash");
    }
    return errors.empty();
}

static bool parse_anchor_identity(const std::string &path,
                                  CoredataPackRecordView &out,
                                  std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvReader r(out.payload.empty() ? 0 : &out.payload[0], out.payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_kind = false;
    bool has_system_class = false;
    bool has_region_type = false;
    bool has_evidence = false;
    bool has_profile = false;
    bool has_weight = false;
    u32 kind = 0u;
    u32 tmp_u32 = 0u;

    while (r.next(rec)) {
        switch (rec.tag) {
            case CORE_DATA_ANCHOR_TAG_ID:
                out.id = parse_string_field(rec);
                has_id = true;
                break;
            case CORE_DATA_ANCHOR_TAG_ID_HASH:
                has_id_hash = parse_u64_field(path, rec.tag, rec, out.id_hash, errors);
                break;
            case CORE_DATA_ANCHOR_TAG_KIND:
                has_kind = parse_u32_field(path, rec.tag, rec, kind, errors);
                break;
            case CORE_DATA_ANCHOR_TAG_DISPLAY_NAME:
                (void)parse_string_field(rec);
                break;
            case CORE_DATA_ANCHOR_TAG_SYSTEM_CLASS:
                has_system_class = parse_u32_field(path, rec.tag, rec, tmp_u32, errors);
                break;
            case CORE_DATA_ANCHOR_TAG_REGION_TYPE:
                has_region_type = parse_u32_field(path, rec.tag, rec, tmp_u32, errors);
                break;
            case CORE_DATA_ANCHOR_TAG_EVIDENCE_GRADE:
                has_evidence = parse_u32_field(path, rec.tag, rec, tmp_u32, errors);
                break;
            case CORE_DATA_ANCHOR_TAG_MECH_PROFILE_ID:
                (void)parse_string_field(rec);
                has_profile = true;
                break;
            case CORE_DATA_ANCHOR_TAG_ANCHOR_WEIGHT:
                has_weight = parse_u32_field(path, rec.tag, rec, tmp_u32, errors);
                break;
            case CORE_DATA_ANCHOR_TAG_TAG:
                (void)parse_string_field(rec);
                break;
            case CORE_DATA_ANCHOR_TAG_PRESENTATION_POS:
                if (rec.len != 12u) {
                    add_error(errors, path, "anchor_present_pos_invalid", "presentational_position");
                }
                break;
            default:
                add_error(errors, path, "anchor_unknown_tag", "unknown tag");
                break;
        }
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "anchor_truncated", "anchor TLV truncated");
    }
    if (!has_id || !has_id_hash || !has_kind || !has_evidence || !has_profile || !has_weight) {
        add_error(errors, path, "anchor_missing_field", "required anchor field missing");
    }
    if (has_kind) {
        if (kind == CORE_DATA_KIND_SYSTEM && !has_system_class) {
            add_error(errors, path, "anchor_missing_field", "system_class");
        }
        if (kind == CORE_DATA_KIND_REGION && !has_region_type) {
            add_error(errors, path, "anchor_missing_field", "region_type");
        }
    }
    return errors.empty();
}

static bool parse_edge_identity(const std::string &path,
                                CoredataPackRecordView &out,
                                std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvReader r(out.payload.empty() ? 0 : &out.payload[0], out.payload.size());
    dom::core_tlv::TlvRecord rec;
    std::string src_id;
    std::string dst_id;
    u64 src_hash = 0ull;
    u64 dst_hash = 0ull;
    u64 tmp_u64 = 0ull;
    bool has_src = false;
    bool has_dst = false;
    bool has_src_hash = false;
    bool has_dst_hash = false;
    bool has_duration = false;
    bool has_cost = false;
    bool has_cost_hash = false;

    while (r.next(rec)) {
        switch (rec.tag) {
            case CORE_DATA_EDGE_TAG_SRC_ID:
                src_id = parse_string_field(rec);
                has_src = true;
                break;
            case CORE_DATA_EDGE_TAG_SRC_ID_HASH:
                has_src_hash = parse_u64_field(path, rec.tag, rec, src_hash, errors);
                break;
            case CORE_DATA_EDGE_TAG_DST_ID:
                dst_id = parse_string_field(rec);
                has_dst = true;
                break;
            case CORE_DATA_EDGE_TAG_DST_ID_HASH:
                has_dst_hash = parse_u64_field(path, rec.tag, rec, dst_hash, errors);
                break;
            case CORE_DATA_EDGE_TAG_DURATION_TICKS:
                has_duration = parse_u64_field(path, rec.tag, rec, tmp_u64, errors);
                break;
            case CORE_DATA_EDGE_TAG_COST_PROFILE_ID:
                (void)parse_string_field(rec);
                has_cost = true;
                break;
            case CORE_DATA_EDGE_TAG_COST_PROFILE_HASH:
                has_cost_hash = parse_u64_field(path, rec.tag, rec, tmp_u64, errors);
                break;
            case CORE_DATA_EDGE_TAG_HAZARD_PROFILE_ID:
                (void)parse_string_field(rec);
                break;
            case CORE_DATA_EDGE_TAG_HAZARD_PROFILE_HASH:
                (void)parse_u64_field(path, rec.tag, rec, tmp_u64, errors);
                break;
            default:
                add_error(errors, path, "edge_unknown_tag", "unknown tag");
                break;
        }
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "edge_truncated", "edge TLV truncated");
    }
    if (!has_src || !has_dst || !has_src_hash || !has_dst_hash || !has_duration ||
        !has_cost || !has_cost_hash) {
        add_error(errors, path, "edge_missing_field", "required edge field missing");
    }
    if (has_src && has_dst) {
        std::string key = src_id + "->" + dst_id;
        u64 key_hash = 0ull;
        if (dom_id_hash64(key.c_str(), (u32)key.size(), &key_hash) == DOM_SPACETIME_OK) {
            out.id = key;
            out.id_hash = key_hash;
        }
    }
    return errors.empty();
}

static bool parse_rules_record(const std::string &path,
                               const CoredataPackRecordView &rec_view,
                               std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvReader r(rec_view.payload.empty() ? 0 : &rec_view.payload[0],
                               rec_view.payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_sys_min = false;
    bool has_sys_max = false;
    bool has_red = false;
    bool has_bin = false;
    bool has_exotic = false;
    u32 tmp_u32 = 0u;
    i32 tmp_i32 = 0;
    while (r.next(rec)) {
        switch (rec.tag) {
            case CORE_DATA_RULES_TAG_SYS_MIN:
                has_sys_min = parse_u32_field(path, rec.tag, rec, tmp_u32, errors);
                break;
            case CORE_DATA_RULES_TAG_SYS_MAX:
                has_sys_max = parse_u32_field(path, rec.tag, rec, tmp_u32, errors);
                break;
            case CORE_DATA_RULES_TAG_RED_DWARF_RATIO:
                has_red = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_RULES_TAG_BINARY_RATIO:
                has_bin = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_RULES_TAG_EXOTIC_RATIO:
                has_exotic = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_RULES_TAG_CLUSTER_DENSITY:
            case CORE_DATA_RULES_TAG_METALLICITY_BIAS:
            case CORE_DATA_RULES_TAG_HAZARD_FREQUENCY:
                if (rec.len > 0u) {
                    dom::core_tlv::TlvReader inner(rec.payload, rec.len);
                    dom::core_tlv::TlvRecord inner_rec;
                    bool has_region = false;
                    bool has_value = false;
                    while (inner.next(inner_rec)) {
                        if (inner_rec.tag == CORE_DATA_RULES_ENTRY_TAG_REGION_TYPE) {
                            has_region = parse_u32_field(path, inner_rec.tag, inner_rec, tmp_u32, errors);
                        } else if (inner_rec.tag == CORE_DATA_RULES_ENTRY_TAG_VALUE_Q16) {
                            has_value = parse_i32_field(path, inner_rec.tag, inner_rec, tmp_i32, errors);
                        } else {
                            add_error(errors, path, "rules_entry_unknown_tag", "unknown tag");
                        }
                    }
                    if (inner.remaining() != 0u) {
                        add_error(errors, path, "rules_entry_truncated", "rules entry truncated");
                    }
                    if (!has_region || !has_value) {
                        add_error(errors, path, "rules_entry_missing_field", "rules entry missing field");
                    }
                }
                break;
            default:
                add_error(errors, path, "rules_unknown_tag", "unknown tag");
                break;
        }
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "rules_truncated", "rules TLV truncated");
    }
    if (!has_sys_min || !has_sys_max || !has_red || !has_bin || !has_exotic) {
        add_error(errors, path, "rules_missing_field", "required rules field missing");
    }
    return errors.empty();
}

static bool parse_mech_system_identity(const std::string &path,
                                       CoredataPackRecordView &out,
                                       std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvReader r(out.payload.empty() ? 0 : &out.payload[0], out.payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_nav = false;
    bool has_debris = false;
    bool has_rad = false;
    bool has_warp = false;
    bool has_survey = false;
    i32 tmp_i32 = 0;
    u64 tmp_u64 = 0ull;
    while (r.next(rec)) {
        switch (rec.tag) {
            case CORE_DATA_MECH_SYS_TAG_ID:
                out.id = parse_string_field(rec);
                has_id = true;
                break;
            case CORE_DATA_MECH_SYS_TAG_ID_HASH:
                has_id_hash = parse_u64_field(path, rec.tag, rec, out.id_hash, errors);
                break;
            case CORE_DATA_MECH_SYS_TAG_NAV_INSTABILITY:
                has_nav = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SYS_TAG_DEBRIS_COLLISION:
                has_debris = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SYS_TAG_RADIATION_BASELINE:
                has_rad = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SYS_TAG_WARP_CAP:
                has_warp = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SYS_TAG_SURVEY_DIFFICULTY:
                has_survey = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SYS_TAG_SUPERNOVA_TICKS:
                (void)parse_u64_field(path, rec.tag, rec, tmp_u64, errors);
                break;
            default:
                add_error(errors, path, "mech_system_unknown_tag", "unknown tag");
                break;
        }
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "mech_system_truncated", "system profile TLV truncated");
    }
    if (!has_id || !has_id_hash || !has_nav || !has_debris || !has_rad || !has_warp || !has_survey) {
        add_error(errors, path, "mech_system_missing_field", "required system profile field missing");
    }
    return errors.empty();
}

static bool parse_mech_site_identity(const std::string &path,
                                     CoredataPackRecordView &out,
                                     std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvReader r(out.payload.empty() ? 0 : &out.payload[0], out.payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_rad = false;
    bool has_press = false;
    bool has_corrosion = false;
    bool has_temp = false;
    i32 tmp_i32 = 0;
    while (r.next(rec)) {
        switch (rec.tag) {
            case CORE_DATA_MECH_SITE_TAG_ID:
                out.id = parse_string_field(rec);
                has_id = true;
                break;
            case CORE_DATA_MECH_SITE_TAG_ID_HASH:
                has_id_hash = parse_u64_field(path, rec.tag, rec, out.id_hash, errors);
                break;
            case CORE_DATA_MECH_SITE_TAG_HAZARD_RAD:
                has_rad = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SITE_TAG_HAZARD_PRESS:
                has_press = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SITE_TAG_CORROSION_RATE:
                has_corrosion = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SITE_TAG_TEMP_EXTREME:
                has_temp = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_MECH_SITE_TAG_RESOURCE_YIELD:
                if (rec.len > 0u) {
                    dom::core_tlv::TlvReader inner(rec.payload, rec.len);
                    dom::core_tlv::TlvRecord inner_rec;
                    bool has_res = false;
                    bool has_mod = false;
                    while (inner.next(inner_rec)) {
                        if (inner_rec.tag == CORE_DATA_MECH_SITE_RES_TAG_ID) {
                            (void)parse_string_field(inner_rec);
                            has_res = true;
                        } else if (inner_rec.tag == CORE_DATA_MECH_SITE_RES_TAG_MOD_Q16) {
                            has_mod = parse_i32_field(path, inner_rec.tag, inner_rec, tmp_i32, errors);
                        } else {
                            add_error(errors, path, "mech_site_resource_unknown_tag", "unknown tag");
                        }
                    }
                    if (inner.remaining() != 0u) {
                        add_error(errors, path, "mech_site_resource_truncated", "resource entry truncated");
                    }
                    if (!has_res || !has_mod) {
                        add_error(errors, path, "mech_site_resource_missing_field", "resource entry missing");
                    }
                }
                break;
            case CORE_DATA_MECH_SITE_TAG_ACCESS_CONSTRAINT:
                (void)parse_string_field(rec);
                break;
            default:
                add_error(errors, path, "mech_site_unknown_tag", "unknown tag");
                break;
        }
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "mech_site_truncated", "site profile TLV truncated");
    }
    if (!has_id || !has_id_hash || !has_rad || !has_press || !has_corrosion || !has_temp) {
        add_error(errors, path, "mech_site_missing_field", "required site profile field missing");
    }
    return errors.empty();
}

static bool parse_astro_identity(const std::string &path,
                                 CoredataPackRecordView &out,
                                 std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvReader r(out.payload.empty() ? 0 : &out.payload[0], out.payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_mu = false;
    bool has_mu_exp = false;
    u64 tmp_u64 = 0ull;
    i32 tmp_i32 = 0;
    while (r.next(rec)) {
        switch (rec.tag) {
            case CORE_DATA_ASTRO_TAG_ID:
                out.id = parse_string_field(rec);
                has_id = true;
                break;
            case CORE_DATA_ASTRO_TAG_ID_HASH:
                has_id_hash = parse_u64_field(path, rec.tag, rec, out.id_hash, errors);
                break;
            case CORE_DATA_ASTRO_TAG_RADIUS_M:
                (void)parse_u64_field(path, rec.tag, rec, tmp_u64, errors);
                break;
            case CORE_DATA_ASTRO_TAG_MU_MANTISSA:
                has_mu = parse_u64_field(path, rec.tag, rec, tmp_u64, errors);
                break;
            case CORE_DATA_ASTRO_TAG_MU_EXP10:
                has_mu_exp = parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_ASTRO_TAG_ROT_RATE_Q16:
                (void)parse_i32_field(path, rec.tag, rec, tmp_i32, errors);
                break;
            case CORE_DATA_ASTRO_TAG_ATMOS_PROFILE_ID:
                (void)parse_string_field(rec);
                break;
            default:
                add_error(errors, path, "astro_unknown_tag", "unknown tag");
                break;
        }
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "astro_truncated", "astro TLV truncated");
    }
    if (!has_id || !has_id_hash || !has_mu || !has_mu_exp) {
        add_error(errors, path, "astro_missing_field", "required astro field missing");
    }
    return errors.empty();
}

static bool parse_manifest(const std::string &path,
                           const unsigned char *data,
                           u32 len,
                           CoredataManifestView &out,
                           std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvReader r(data, len);
    dom::core_tlv::TlvRecord rec;
    bool has_schema = false;
    bool has_pack_id = false;
    bool has_pack_version = false;
    bool has_pack_schema = false;
    bool has_content_hash = false;
    bool has_pack_hash = false;

    while (r.next(rec)) {
        switch (rec.tag) {
            case CORE_DATA_MANIFEST_TAG_SCHEMA_VERSION:
                has_schema = parse_u32_field(path, rec.tag, rec, out.schema_version, errors);
                break;
            case CORE_DATA_MANIFEST_TAG_PACK_ID:
                out.pack_id = parse_string_field(rec);
                has_pack_id = true;
                break;
            case CORE_DATA_MANIFEST_TAG_PACK_VERSION_NUM:
                has_pack_version = parse_u32_field(path, rec.tag, rec, out.pack_version_num, errors);
                break;
            case CORE_DATA_MANIFEST_TAG_PACK_VERSION_STR:
                out.pack_version_str = parse_string_field(rec);
                break;
            case CORE_DATA_MANIFEST_TAG_PACK_SCHEMA_VERSION:
                has_pack_schema = parse_u32_field(path, rec.tag, rec, out.pack_schema_version, errors);
                break;
            case CORE_DATA_MANIFEST_TAG_CONTENT_HASH:
                has_content_hash = parse_u64_field(path, rec.tag, rec, out.content_hash, errors);
                break;
            case CORE_DATA_MANIFEST_TAG_PACK_HASH:
                has_pack_hash = parse_u64_field(path, rec.tag, rec, out.pack_hash, errors);
                break;
            case CORE_DATA_MANIFEST_TAG_RECORD: {
                dom::core_tlv::TlvReader inner(rec.payload, rec.len);
                dom::core_tlv::TlvRecord inner_rec;
                CoredataManifestRecordView view;
                bool has_type = false;
                bool has_version = false;
                bool has_hash = false;
                while (inner.next(inner_rec)) {
                    switch (inner_rec.tag) {
                        case CORE_DATA_MANIFEST_REC_TAG_TYPE:
                            has_type = parse_u32_field(path, inner_rec.tag, inner_rec, view.type_id, errors);
                            break;
                        case CORE_DATA_MANIFEST_REC_TAG_VERSION:
                            has_version = parse_u32_field(path, inner_rec.tag, inner_rec, view.version, errors);
                            break;
                        case CORE_DATA_MANIFEST_REC_TAG_ID:
                            view.id = parse_string_field(inner_rec);
                            break;
                        case CORE_DATA_MANIFEST_REC_TAG_ID_HASH:
                            (void)parse_u64_field(path, inner_rec.tag, inner_rec, view.id_hash, errors);
                            break;
                        case CORE_DATA_MANIFEST_REC_TAG_RECORD_HASH:
                            has_hash = parse_u64_field(path, inner_rec.tag, inner_rec, view.record_hash, errors);
                            break;
                        default:
                            add_error(errors, path, "manifest_record_unknown_tag", "unknown tag");
                            break;
                    }
                }
                if (inner.remaining() != 0u) {
                    add_error(errors, path, "manifest_record_truncated", "manifest record truncated");
                }
                if (!has_type || !has_version || !has_hash) {
                    add_error(errors, path, "manifest_record_missing_field", "record missing field");
                }
                out.records.push_back(view);
                break;
            }
            default:
                add_error(errors, path, "manifest_unknown_tag", "unknown tag");
                break;
        }
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "manifest_truncated", "manifest TLV truncated");
    }
    if (!has_schema || !has_pack_id || !has_pack_version || !has_pack_schema ||
        !has_content_hash || !has_pack_hash) {
        add_error(errors, path, "manifest_missing_field", "manifest missing field");
    }
    return errors.empty();
}

static bool parse_record_identity(const std::string &path,
                                  CoredataPackRecordView &view,
                                  std::vector<CoredataError> &errors) {
    switch (view.type_id) {
        case CORE_DATA_REC_PACK_META:
            return true;
        case CORE_DATA_REC_COSMO_ANCHOR:
            return parse_anchor_identity(path, view, errors);
        case CORE_DATA_REC_COSMO_EDGE:
            return parse_edge_identity(path, view, errors);
        case CORE_DATA_REC_COSMO_RULES:
            return parse_rules_record(path, view, errors);
        case CORE_DATA_REC_MECH_SYSTEM:
            return parse_mech_system_identity(path, view, errors);
        case CORE_DATA_REC_MECH_SITE:
            return parse_mech_site_identity(path, view, errors);
        case CORE_DATA_REC_ASTRO_BODY:
            return parse_astro_identity(path, view, errors);
        default:
            add_error(errors, path, "record_unknown_type", "unknown record type");
            return false;
    }
}

} // namespace

bool coredata_validate_load_authoring(const std::string &root,
                                      CoredataData &out,
                                      std::vector<CoredataError> &errors) {
    return coredata_load_all(root, out, errors);
}

bool coredata_validate_load_pack(const std::string &path,
                                 CoredataPackView &out_pack,
                                 std::vector<CoredataError> &errors) {
    std::vector<unsigned char> bytes;
    std::string err;
    dom::core_tlv::TlvReader r(0, 0);
    dom::core_tlv::TlvRecord rec;

    errors.clear();
    out_pack = CoredataPackView();

    if (!read_file_bytes(path, bytes, err)) {
        add_error(errors, path, "file_error", err);
        return false;
    }
    out_pack.pack_hash = dom::core_tlv::tlv_fnv1a64(bytes.empty() ? 0 : &bytes[0], bytes.size());

    r = dom::core_tlv::TlvReader(bytes.empty() ? 0 : &bytes[0], bytes.size());
    while (r.next(rec)) {
        CoredataPackRecordView view;
        view.type_id = rec.tag;
        if (rec.len > 0u && rec.payload) {
            view.payload.assign(rec.payload, rec.payload + rec.len);
        }
        view.record_hash = hash_record(view.type_id, (u16)CORE_DATA_REC_VERSION_V1, view.payload);
        if (!parse_record_identity(path, view, errors)) {
            /* keep going for complete error reporting */
        }
        if (view.type_id == CORE_DATA_REC_PACK_META) {
            if (out_pack.has_pack_meta) {
                add_error(errors, path, "pack_meta_duplicate", "multiple pack meta records");
            } else {
                out_pack.has_pack_meta = true;
                (void)parse_pack_meta(path, rec.payload, rec.len, out_pack, errors);
            }
        }
        out_pack.records.push_back(view);
    }
    if (r.remaining() != 0u) {
        add_error(errors, path, "pack_truncated", "pack TLV truncated");
    }
    if (!out_pack.has_pack_meta) {
        add_error(errors, path, "pack_meta_missing", "pack meta missing");
    }
    return errors.empty();
}

bool coredata_validate_load_manifest(const std::string &path,
                                     CoredataManifestView &out_manifest,
                                     std::vector<CoredataError> &errors) {
    std::vector<unsigned char> bytes;
    std::string err;
    errors.clear();
    out_manifest = CoredataManifestView();

    if (!read_file_bytes(path, bytes, err)) {
        add_error(errors, path, "file_error", err);
        return false;
    }
    out_manifest.present = true;
    (void)parse_manifest(path, bytes.empty() ? 0 : &bytes[0],
                         (u32)bytes.size(), out_manifest, errors);
    return errors.empty();
}

} // namespace tools
} // namespace dom
