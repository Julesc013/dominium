/*
FILE: source/dominium/game/runtime/dom_atmos_provider.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/atmos_provider
RESPONSIBILITY: Atmosphere provider contracts and profile helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_ATMOS_PROVIDER_H
#define DOM_ATMOS_PROVIDER_H

#include "domino/core/fixed.h"
#include "runtime/dom_media_provider.h"

#ifdef __cplusplus
#include <vector>
#endif

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_ATMOS_OK = 0,
    DOM_ATMOS_ERR = -1,
    DOM_ATMOS_INVALID_ARGUMENT = -2,
    DOM_ATMOS_INVALID_DATA = -3
};

enum {
    DOM_ATMOS_PROFILE_V1 = 1u
};

enum {
    DOM_ATMOS_TLV_TOP_ALT_M = 0x0101u,
    DOM_ATMOS_TLV_SEGMENT = 0x0102u
};

enum {
    DOM_ATMOS_PROFILE_MAX_SEGMENTS = 32u
};

typedef struct dom_atmos_profile_segment {
    q48_16 altitude_m;
    q16_16 density_q16;
    q16_16 pressure_q16;
    q16_16 temperature_q16;
} dom_atmos_profile_segment;

int dom_atmos_register_profile_v1(dom_media_registry *registry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#ifdef __cplusplus
int dom_atmos_profile_build_tlv(const dom_atmos_profile_segment *segments,
                                u32 segment_count,
                                q48_16 top_altitude_m,
                                std::vector<unsigned char> &out_tlv);
#endif

#endif /* DOM_ATMOS_PROVIDER_H */
