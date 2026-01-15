/*
FILE: source/dominium/common/dom_caps_split.cpp
MODULE: Dominium
PURPOSE: SIM_CAPS and PERF_CAPS canonical TLV helpers + hashes.
*/
#include "dominium/caps_split.h"

#include "dominium/core_tlv.h"

namespace {

enum {
    SIM_CAPS_TLV_TAG_DET_GRADE = 2u,
    SIM_CAPS_TLV_TAG_MATH_PROFILE = 3u,
    SIM_CAPS_TLV_TAG_SIM_FLAGS = 4u
};

enum {
    PERF_CAPS_TLV_TAG_TIER_PROFILE = 2u,
    PERF_CAPS_TLV_TAG_PERF_FLAGS = 3u
};

static u32 sanitize_tier(u32 tier_profile) {
    if (tier_profile == dom::DOM_PERF_TIER_MODERN ||
        tier_profile == dom::DOM_PERF_TIER_SERVER) {
        return tier_profile;
    }
    return dom::DOM_PERF_TIER_BASELINE;
}

} /* namespace */

namespace dom {

DomSimCaps::DomSimCaps() {
    dom_sim_caps_init_default(*this);
}

DomPerfCaps::DomPerfCaps() {
    dom_perf_caps_init_default(*this, DOM_PERF_TIER_BASELINE);
}

void dom_sim_caps_init_default(DomSimCaps &caps) {
    caps.struct_size = (u32)sizeof(DomSimCaps);
    caps.struct_version = DOM_SIM_CAPS_VERSION;
    caps.determinism_grade = 0u;
    caps.math_profile = DOM_SIM_MATH_PROFILE_FIXED_V1;
    caps.sim_flags = 0u;
}

void dom_perf_caps_init_default(DomPerfCaps &caps, u32 tier_profile) {
    caps.struct_size = (u32)sizeof(DomPerfCaps);
    caps.struct_version = DOM_PERF_CAPS_VERSION;
    caps.tier_profile = sanitize_tier(tier_profile);
    caps.perf_flags = 0u;
}

bool dom_sim_caps_to_tlv(const DomSimCaps &caps, std::vector<unsigned char> &out) {
    core_tlv::TlvWriter w;
    w.add_u32(core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_SIM_CAPS_VERSION);
    w.add_u32(SIM_CAPS_TLV_TAG_DET_GRADE, caps.determinism_grade);
    w.add_u32(SIM_CAPS_TLV_TAG_MATH_PROFILE, caps.math_profile);
    w.add_u32(SIM_CAPS_TLV_TAG_SIM_FLAGS, caps.sim_flags);
    out = w.bytes();
    return true;
}

bool dom_sim_caps_from_tlv(const unsigned char *data, u32 len, DomSimCaps &out) {
    core_tlv::TlvReader r(data, (size_t)len);
    core_tlv::TlvRecord rec;
    u32 schema = 0u;
    u32 det_grade = 0u;
    u32 math_profile = 0u;
    u32 sim_flags = 0u;
    bool have_schema = false;
    bool have_det = false;
    bool have_math = false;
    bool have_flags = false;

    while (r.next(rec)) {
        switch (rec.tag) {
        case core_tlv::CORE_TLV_TAG_SCHEMA_VERSION:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, schema)) {
                have_schema = true;
            }
            break;
        case SIM_CAPS_TLV_TAG_DET_GRADE:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, det_grade)) {
                have_det = true;
            }
            break;
        case SIM_CAPS_TLV_TAG_MATH_PROFILE:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, math_profile)) {
                have_math = true;
            }
            break;
        case SIM_CAPS_TLV_TAG_SIM_FLAGS:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, sim_flags)) {
                have_flags = true;
            }
            break;
        default:
            break;
        }
    }

    if (!have_schema || schema != DOM_SIM_CAPS_VERSION || !have_det || !have_math) {
        return false;
    }

    out.struct_size = (u32)sizeof(DomSimCaps);
    out.struct_version = schema;
    out.determinism_grade = det_grade;
    out.math_profile = math_profile;
    out.sim_flags = have_flags ? sim_flags : 0u;
    return true;
}

u64 dom_sim_caps_hash64(const DomSimCaps &caps) {
    std::vector<unsigned char> bytes;
    if (!dom_sim_caps_to_tlv(caps, bytes)) {
        return 0ull;
    }
    return core_tlv::tlv_fnv1a64(bytes.empty() ? (const unsigned char *)0 : &bytes[0],
                                 bytes.size());
}

bool dom_perf_caps_to_tlv(const DomPerfCaps &caps, std::vector<unsigned char> &out) {
    core_tlv::TlvWriter w;
    w.add_u32(core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_PERF_CAPS_VERSION);
    w.add_u32(PERF_CAPS_TLV_TAG_TIER_PROFILE, sanitize_tier(caps.tier_profile));
    w.add_u32(PERF_CAPS_TLV_TAG_PERF_FLAGS, caps.perf_flags);
    out = w.bytes();
    return true;
}

bool dom_perf_caps_from_tlv(const unsigned char *data, u32 len, DomPerfCaps &out) {
    core_tlv::TlvReader r(data, (size_t)len);
    core_tlv::TlvRecord rec;
    u32 schema = 0u;
    u32 tier = 0u;
    u32 perf_flags = 0u;
    bool have_schema = false;
    bool have_tier = false;
    bool have_flags = false;

    while (r.next(rec)) {
        switch (rec.tag) {
        case core_tlv::CORE_TLV_TAG_SCHEMA_VERSION:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, schema)) {
                have_schema = true;
            }
            break;
        case PERF_CAPS_TLV_TAG_TIER_PROFILE:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, tier)) {
                have_tier = true;
            }
            break;
        case PERF_CAPS_TLV_TAG_PERF_FLAGS:
            if (core_tlv::tlv_read_u32_le(rec.payload, rec.len, perf_flags)) {
                have_flags = true;
            }
            break;
        default:
            break;
        }
    }

    if (!have_schema || schema != DOM_PERF_CAPS_VERSION || !have_tier) {
        return false;
    }

    out.struct_size = (u32)sizeof(DomPerfCaps);
    out.struct_version = schema;
    out.tier_profile = sanitize_tier(tier);
    out.perf_flags = have_flags ? perf_flags : 0u;
    return true;
}

u64 dom_perf_caps_hash64(const DomPerfCaps &caps) {
    std::vector<unsigned char> bytes;
    if (!dom_perf_caps_to_tlv(caps, bytes)) {
        return 0ull;
    }
    return core_tlv::tlv_fnv1a64(bytes.empty() ? (const unsigned char *)0 : &bytes[0],
                                 bytes.size());
}

} /* namespace dom */
