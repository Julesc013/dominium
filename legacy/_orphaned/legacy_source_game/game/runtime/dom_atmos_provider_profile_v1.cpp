/*
FILE: source/dominium/game/runtime/dom_atmos_provider_profile_v1.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/atmos_provider_profile_v1
RESPONSIBILITY: Deterministic piecewise atmosphere profile provider (v1).
*/
#include "runtime/dom_atmos_provider.h"

#include <cstring>
#include <climits>

#include "dominium/core_tlv.h"

namespace {

struct AtmosProfile {
    q48_16 top_altitude_m;
    u32 segment_count;
    dom_atmos_profile_segment segments[DOM_ATMOS_PROFILE_MAX_SEGMENTS];
};

static i32 read_i32_le(const unsigned char *p) {
    return (i32)((u32)p[0] |
                 ((u32)p[1] << 8) |
                 ((u32)p[2] << 16) |
                 ((u32)p[3] << 24));
}

static i64 read_i64_le(const unsigned char *p) {
    u64 lo = (u64)read_i32_le(p);
    u64 hi = (u64)read_i32_le(p + 4);
    return (i64)(lo | (hi << 32));
}

static int parse_profile(const dom_media_binding *binding, AtmosProfile *out_profile) {
    if (!binding || !out_profile) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    if (!binding->params || binding->params_len == 0u) {
        return DOM_MEDIA_INVALID_DATA;
    }

    dom::core_tlv::TlvReader reader(binding->params, binding->params_len);
    dom::core_tlv::TlvRecord rec;
    u32 schema_version = 0u;
    u32 seg_count = 0u;
    q48_16 top_alt = 0;

    std::memset(out_profile, 0, sizeof(*out_profile));

    while (reader.next(rec)) {
        if (rec.tag == dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, schema_version);
        } else if (rec.tag == DOM_ATMOS_TLV_TOP_ALT_M) {
            if (rec.len != 8u) {
                return DOM_MEDIA_INVALID_DATA;
            }
            top_alt = (q48_16)read_i64_le(rec.payload);
        } else if (rec.tag == DOM_ATMOS_TLV_SEGMENT) {
            if (rec.len != 20u) {
                return DOM_MEDIA_INVALID_DATA;
            }
            if (seg_count >= DOM_ATMOS_PROFILE_MAX_SEGMENTS) {
                return DOM_MEDIA_INVALID_DATA;
            }
            dom_atmos_profile_segment &seg = out_profile->segments[seg_count];
            seg.altitude_m = (q48_16)read_i64_le(rec.payload + 0);
            seg.density_q16 = (q16_16)read_i32_le(rec.payload + 8);
            seg.pressure_q16 = (q16_16)read_i32_le(rec.payload + 12);
            seg.temperature_q16 = (q16_16)read_i32_le(rec.payload + 16);
            ++seg_count;
        }
    }

    if (schema_version != DOM_ATMOS_PROFILE_V1) {
        return DOM_MEDIA_INVALID_DATA;
    }
    if (seg_count < 2u) {
        return DOM_MEDIA_INVALID_DATA;
    }

    if (top_alt <= 0) {
        top_alt = out_profile->segments[seg_count - 1u].altitude_m;
    }
    if (top_alt <= 0) {
        return DOM_MEDIA_INVALID_DATA;
    }

    for (u32 i = 0u; i < seg_count; ++i) {
        const dom_atmos_profile_segment &seg = out_profile->segments[i];
        if (seg.density_q16 < 0 || seg.pressure_q16 < 0 || seg.temperature_q16 <= 0) {
            return DOM_MEDIA_INVALID_DATA;
        }
        if (i > 0u) {
            if (seg.altitude_m <= out_profile->segments[i - 1u].altitude_m) {
                return DOM_MEDIA_INVALID_DATA;
            }
        }
    }

    out_profile->top_altitude_m = top_alt;
    out_profile->segment_count = seg_count;
    return DOM_MEDIA_OK;
}

static q16_16 lerp_q16(q16_16 a, q16_16 b, q16_16 t) {
    i64 delta = (i64)b - (i64)a;
    i64 scaled = (delta * (i64)t) >> 16;
    i64 value = (i64)a + scaled;
    if (value > (i64)INT_MAX) {
        value = (i64)INT_MAX;
    }
    if (value < (i64)INT_MIN) {
        value = (i64)INT_MIN;
    }
    return (q16_16)value;
}

static q16_16 fraction_q16(q48_16 num, q48_16 den) {
    if (den <= 0) {
        return 0;
    }
    i64 n = (i64)num;
    i64 d = (i64)den;
    if (n <= 0) {
        return 0;
    }
    if (n >= d) {
        return d_q16_16_from_int(1);
    }
    if (n > (INT64_MAX >> 16)) {
        n >>= 4;
        d >>= 4;
    }
    if (d <= 0) {
        return 0;
    }
    return (q16_16)((n << 16) / d);
}

static int atmos_validate(dom_body_id body_id, const dom_media_binding *binding) {
    AtmosProfile profile;
    (void)body_id;
    return parse_profile(binding, &profile);
}

static int atmos_sample(dom_body_id body_id,
                        const dom_media_binding *binding,
                        const dom_posseg_q16 *pos_body_fixed,
                        q48_16 altitude_m,
                        dom_tick tick,
                        dom_media_sample *out_sample) {
    AtmosProfile profile;
    int rc;
    (void)body_id;
    (void)pos_body_fixed;
    (void)tick;

    if (!binding || !out_sample) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }

    rc = parse_profile(binding, &profile);
    if (rc != DOM_MEDIA_OK) {
        return rc;
    }

    if (altitude_m < 0) {
        altitude_m = 0;
    }
    if (altitude_m >= profile.top_altitude_m) {
        out_sample->density_q16 = 0;
        out_sample->pressure_q16 = 0;
        out_sample->temperature_q16 =
            profile.segments[profile.segment_count - 1u].temperature_q16;
        std::memset(&out_sample->wind_body_q16, 0, sizeof(out_sample->wind_body_q16));
        out_sample->has_wind = 0u;
        return DOM_MEDIA_OK;
    }

    u32 idx = 0u;
    for (u32 i = 1u; i < profile.segment_count; ++i) {
        if (altitude_m < profile.segments[i].altitude_m) {
            idx = i - 1u;
            break;
        }
    }
    if (idx >= profile.segment_count - 1u) {
        idx = profile.segment_count - 2u;
    }

    const dom_atmos_profile_segment &a = profile.segments[idx];
    const dom_atmos_profile_segment &b = profile.segments[idx + 1u];
    q48_16 delta = b.altitude_m - a.altitude_m;
    q48_16 offset = altitude_m - a.altitude_m;
    q16_16 t = fraction_q16(offset, delta);

    out_sample->density_q16 = lerp_q16(a.density_q16, b.density_q16, t);
    out_sample->pressure_q16 = lerp_q16(a.pressure_q16, b.pressure_q16, t);
    out_sample->temperature_q16 = lerp_q16(a.temperature_q16, b.temperature_q16, t);
    std::memset(&out_sample->wind_body_q16, 0, sizeof(out_sample->wind_body_q16));
    out_sample->has_wind = 0u;
    return DOM_MEDIA_OK;
}

} // namespace

int dom_atmos_register_profile_v1(dom_media_registry *registry) {
    dom_media_provider_vtbl vtbl;
    if (!registry) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    std::memset(&vtbl, 0, sizeof(vtbl));
    vtbl.api_version = DOM_ATMOS_PROFILE_V1;
    vtbl.validate = atmos_validate;
    vtbl.sample = atmos_sample;
    return dom_media_registry_register_provider(registry,
                                                DOM_MEDIA_KIND_ATMOSPHERE,
                                                "profile_v1",
                                                &vtbl);
}
