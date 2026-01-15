/*
FILE: include/dominium/caps_split.h
MODULE: Dominium
PURPOSE: SIM_CAPS and PERF_CAPS canonical structs + TLV helpers.
NOTES: SIM_CAPS are identity-bound; PERF_CAPS are negotiable and non-sim.
*/
#ifndef DOMINIUM_CAPS_SPLIT_H
#define DOMINIUM_CAPS_SPLIT_H

#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {

enum {
    DOM_SIM_CAPS_VERSION = 1u,
    DOM_PERF_CAPS_VERSION = 1u
};

enum DomSimMathProfile {
    DOM_SIM_MATH_PROFILE_FIXED_V1 = 1u
};

enum DomPerfTierProfile {
    DOM_PERF_TIER_BASELINE = 0u,
    DOM_PERF_TIER_MODERN = 1u,
    DOM_PERF_TIER_SERVER = 2u
};

struct DomSimCaps {
    u32 struct_size;
    u32 struct_version;
    u32 determinism_grade;
    u32 math_profile;
    u32 sim_flags;

    DomSimCaps();
};

struct DomPerfCaps {
    u32 struct_size;
    u32 struct_version;
    u32 tier_profile;
    u32 perf_flags;

    DomPerfCaps();
};

void dom_sim_caps_init_default(DomSimCaps &caps);
void dom_perf_caps_init_default(DomPerfCaps &caps, u32 tier_profile);

bool dom_sim_caps_to_tlv(const DomSimCaps &caps, std::vector<unsigned char> &out);
bool dom_sim_caps_from_tlv(const unsigned char *data, u32 len, DomSimCaps &out);
u64 dom_sim_caps_hash64(const DomSimCaps &caps);

bool dom_perf_caps_to_tlv(const DomPerfCaps &caps, std::vector<unsigned char> &out);
bool dom_perf_caps_from_tlv(const unsigned char *data, u32 len, DomPerfCaps &out);
u64 dom_perf_caps_hash64(const DomPerfCaps &caps);

} /* namespace dom */

#endif /* DOMINIUM_CAPS_SPLIT_H */
