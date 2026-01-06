/*
FILE: source/dominium/common/dom_caps.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_caps
RESPONSIBILITY: SIM_CAPS/PERF_CAPS compatibility helpers + identity digest utilities.
*/
#include "dom_caps.h"

#include "dominium/core_tlv.h"

namespace {

enum {
    DOM_IDENTITY_TLV_VERSION = 1u
};

enum {
    DOM_IDENTITY_TAG_SIM_CAPS_HASH = 2u,
    DOM_IDENTITY_TAG_CONTENT_DIGEST = 3u,
    DOM_IDENTITY_TAG_PROVIDER_BINDINGS_HASH = 4u
};

} // namespace

namespace dom {

bool dom_sim_caps_equal(const DomSimCaps &a, const DomSimCaps &b) {
    return a.struct_version == b.struct_version &&
           a.determinism_grade == b.determinism_grade &&
           a.math_profile == b.math_profile &&
           a.sim_flags == b.sim_flags;
}

bool dom_sim_caps_compatible(const DomSimCaps &a, const DomSimCaps &b) {
    return dom_sim_caps_equal(a, b);
}

bool dom_perf_caps_equal(const DomPerfCaps &a, const DomPerfCaps &b) {
    return a.struct_version == b.struct_version &&
           a.tier_profile == b.tier_profile &&
           a.perf_flags == b.perf_flags;
}

u64 dom_identity_digest64(const DomSimCaps &sim_caps,
                          const unsigned char *content_hash_bytes,
                          u32 content_hash_len,
                          u64 provider_bindings_hash64) {
    core_tlv::TlvWriter w;
    const u64 sim_caps_hash = dom_sim_caps_hash64(sim_caps);

    w.add_u32(core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_IDENTITY_TLV_VERSION);
    w.add_u64(DOM_IDENTITY_TAG_SIM_CAPS_HASH, sim_caps_hash);
    w.add_bytes(DOM_IDENTITY_TAG_CONTENT_DIGEST,
                content_hash_bytes,
                content_hash_bytes ? content_hash_len : 0u);
    w.add_u64(DOM_IDENTITY_TAG_PROVIDER_BINDINGS_HASH, provider_bindings_hash64);

    const std::vector<unsigned char> &bytes = w.bytes();
    return core_tlv::tlv_fnv1a64(bytes.empty() ? (const unsigned char *)0 : &bytes[0],
                                 bytes.size());
}

} // namespace dom
