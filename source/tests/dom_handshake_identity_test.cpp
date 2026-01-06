/*
FILE: source/tests/dom_handshake_identity_test.cpp
MODULE: Dominium Tests
PURPOSE: Ensure handshake identity digest ignores PERF_CAPS and includes SIM_CAPS.
*/
#include <cstdio>
#include <vector>

#include "dom_caps.h"
#include "dominium/core_tlv.h"
#include "runtime/dom_game_handshake.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static bool build_handshake_bytes(const std::vector<unsigned char> &sim_caps_tlv,
                                  const std::vector<unsigned char> &perf_caps_tlv,
                                  const unsigned char *manifest_hash,
                                  u32 manifest_len,
                                  u64 provider_bindings_hash,
                                  std::vector<unsigned char> &out) {
    dom::core_tlv::TlvWriter w;

    w.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_GAME_HANDSHAKE_TLV_VERSION);
    w.add_u64(DOM_GAME_HANDSHAKE_TLV_TAG_RUN_ID, 42ull);
    w.add_string(DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_ID, "inst1");
    w.add_bytes(DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH, manifest_hash, manifest_len);
    w.add_container(DOM_GAME_HANDSHAKE_TLV_TAG_SIM_CAPS, sim_caps_tlv);
    if (!perf_caps_tlv.empty()) {
        w.add_container(DOM_GAME_HANDSHAKE_TLV_TAG_PERF_CAPS, perf_caps_tlv);
    }
    w.add_u64(DOM_GAME_HANDSHAKE_TLV_TAG_PROVIDER_BINDINGS_HASH, provider_bindings_hash);

    out = w.bytes();
    return !out.empty();
}

int main() {
    dom::DomSimCaps sim;
    dom::DomSimCaps sim2;
    dom::DomPerfCaps perf;
    dom::DomPerfCaps perf2;
    std::vector<unsigned char> sim_tlv;
    std::vector<unsigned char> sim_tlv2;
    std::vector<unsigned char> perf_tlv;
    std::vector<unsigned char> perf_tlv2;
    std::vector<unsigned char> hs_bytes;
    dom::DomGameHandshake hs;
    dom::DomGameHandshake hs2;
    dom::DomGameHandshake hs3;
    unsigned char manifest_hash[8] = { 0x10u, 0x11u, 0x12u, 0x13u, 0x14u, 0x15u, 0x16u, 0x17u };
    const u64 provider_hash = 0x1122334455667788ull;
    u64 h1;
    u64 h2;
    u64 h3;

    dom::dom_sim_caps_init_default(sim);
    dom::dom_perf_caps_init_default(perf, dom::DOM_PERF_TIER_BASELINE);

    if (!dom::dom_sim_caps_to_tlv(sim, sim_tlv)) {
        return fail("sim_caps_tlv");
    }
    if (!dom::dom_perf_caps_to_tlv(perf, perf_tlv)) {
        return fail("perf_caps_tlv");
    }

    if (!build_handshake_bytes(sim_tlv, perf_tlv,
                               manifest_hash, (u32)sizeof(manifest_hash),
                               provider_hash, hs_bytes)) {
        return fail("handshake_build_base");
    }
    if (!dom::dom_game_handshake_from_tlv_bytes(&hs_bytes[0], hs_bytes.size(), hs)) {
        return fail("handshake_parse_base");
    }
    h1 = hs.identity_hash64;

    perf2 = perf;
    perf2.tier_profile = dom::DOM_PERF_TIER_SERVER;
    if (!dom::dom_perf_caps_to_tlv(perf2, perf_tlv2)) {
        return fail("perf_caps_tlv2");
    }
    if (!build_handshake_bytes(sim_tlv, perf_tlv2,
                               manifest_hash, (u32)sizeof(manifest_hash),
                               provider_hash, hs_bytes)) {
        return fail("handshake_build_perf_change");
    }
    if (!dom::dom_game_handshake_from_tlv_bytes(&hs_bytes[0], hs_bytes.size(), hs2)) {
        return fail("handshake_parse_perf_change");
    }
    h2 = hs2.identity_hash64;
    if (h1 != h2) {
        return fail("perf_caps_affects_identity");
    }

    sim2 = sim;
    sim2.sim_flags = sim.sim_flags + 1u;
    if (!dom::dom_sim_caps_to_tlv(sim2, sim_tlv2)) {
        return fail("sim_caps_tlv2");
    }
    if (!build_handshake_bytes(sim_tlv2, perf_tlv,
                               manifest_hash, (u32)sizeof(manifest_hash),
                               provider_hash, hs_bytes)) {
        return fail("handshake_build_sim_change");
    }
    if (!dom::dom_game_handshake_from_tlv_bytes(&hs_bytes[0], hs_bytes.size(), hs3)) {
        return fail("handshake_parse_sim_change");
    }
    h3 = hs3.identity_hash64;
    if (h1 == h3) {
        return fail("sim_caps_missing_from_identity");
    }

    std::printf("dom_handshake_identity_test: OK\n");
    return 0;
}
