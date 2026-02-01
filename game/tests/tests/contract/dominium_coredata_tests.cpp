/*
FILE: tests/contract/dominium_coredata_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Contract tests for coredata pack ingestion and identity boundaries.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

#include "dom_paths.h"
#include "dom_instance.h"
#include "dom_session.h"
#include "dom_game_net.h"

#include "runtime/dom_coredata_load.h"
#include "runtime/dom_cosmo_graph.h"
#include "runtime/dom_system_registry.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_mech_profiles.h"
#include "runtime/dom_game_runtime.h"

#include "coredata_load.h"
#include "coredata_validate.h"
#include "coredata_emit_tlv.h"

#ifndef DOMINIUM_TEST_FIXTURES_DIR
#define DOMINIUM_TEST_FIXTURES_DIR "tests/fixtures"
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static std::string fixture_path(const char *name) {
    return std::string(DOMINIUM_TEST_FIXTURES_DIR) + "/" + name;
}

static int load_data(const std::string &root,
                     dom::tools::CoredataData &out,
                     bool validate) {
    std::vector<dom::tools::CoredataError> errors;
    if (!dom::tools::coredata_load_all(root, out, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 1;
    }
    if (validate) {
        if (!dom::tools::coredata_validate(out, errors)) {
            dom::tools::coredata_errors_print(errors);
            return 1;
        }
    }
    return 0;
}

static int emit_pack(const dom::tools::CoredataData &data,
                     dom::tools::CoredataPack &out_pack) {
    dom::tools::CoredataEmitOptions opts;
    std::vector<dom::tools::CoredataError> errors;
    opts.pack_id = "base_cosmo";
    opts.pack_version_str = "0.1.0";
    opts.pack_version_num = 1u;
    opts.pack_schema_version = 1u;
    if (!dom::tools::coredata_emit_pack(data, opts, out_pack, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 1;
    }
    return 0;
}

static int load_state_from_pack(const dom::tools::CoredataPack &pack,
                                dom_coredata_state &out_state) {
    std::string err;
    int rc = dom_coredata_load_from_bytes(pack.pack_bytes.empty() ? 0 : &pack.pack_bytes[0],
                                          pack.pack_bytes.size(),
                                          &out_state,
                                          &err);
    if (rc != DOM_COREDATA_OK) {
        std::fprintf(stderr, "coredata load error: %s (rc=%d)\n", err.c_str(), rc);
        return 1;
    }
    return 0;
}

struct IngestSummary {
    u64 graph_hash;
    u32 system_count;
    u32 body_count;
    u32 system_profile_count;
    u32 site_profile_count;
};

static int ingest_state(const dom_coredata_state &state,
                        IngestSummary &out) {
    dom::dom_cosmo_graph graph;
    dom::dom_cosmo_graph_config cfg;
    dom_mech_profiles *profiles = 0;
    dom_system_registry *systems = 0;
    dom_body_registry *bodies = 0;
    std::string err;
    int rc = 0;

    if (dom::dom_cosmo_graph_init(&graph, 1u, &cfg) != dom::DOM_COSMO_GRAPH_OK) {
        return fail("cosmo graph init failed");
    }

    profiles = dom_mech_profiles_create();
    systems = dom_system_registry_create();
    bodies = dom_body_registry_create();
    if (!profiles || !systems || !bodies) {
        dom_mech_profiles_destroy(profiles);
        dom_system_registry_destroy(systems);
        dom_body_registry_destroy(bodies);
        return fail("registry create failed");
    }

    rc = dom_coredata_apply_to_registries(&state,
                                          &graph,
                                          profiles,
                                          systems,
                                          bodies,
                                          60u,
                                          &err);
    if (rc != DOM_COREDATA_OK) {
        std::fprintf(stderr, "coredata apply error: %s (rc=%d)\n", err.c_str(), rc);
        dom_mech_profiles_destroy(profiles);
        dom_system_registry_destroy(systems);
        dom_body_registry_destroy(bodies);
        return 1;
    }

    out.graph_hash = dom::dom_cosmo_graph_hash(&graph);
    out.system_count = dom_system_registry_count(systems);
    out.body_count = dom_body_registry_count(bodies);
    out.system_profile_count = dom_mech_profiles_system_count(profiles);
    out.site_profile_count = dom_mech_profiles_site_count(profiles);

    dom_mech_profiles_destroy(profiles);
    dom_system_registry_destroy(systems);
    dom_body_registry_destroy(bodies);
    return 0;
}

static int test_coredata_ingest_determinism(void) {
    dom::tools::CoredataData data;
    dom::tools::CoredataPack pack_a;
    dom::tools::CoredataPack pack_b;
    dom_coredata_state state_a;
    dom_coredata_state state_b;
    IngestSummary summary_a;
    IngestSummary summary_b;

    if (load_data(fixture_path("coredata_min"), data, true) != 0) {
        return fail("load coredata_min failed");
    }
    if (emit_pack(data, pack_a) != 0 || emit_pack(data, pack_b) != 0) {
        return fail("coredata emit failed");
    }
    if (pack_a.pack_bytes.size() != pack_b.pack_bytes.size() ||
        (pack_a.pack_bytes.size() > 0u &&
         std::memcmp(&pack_a.pack_bytes[0],
                     &pack_b.pack_bytes[0],
                     pack_a.pack_bytes.size()) != 0)) {
        return fail("pack bytes not deterministic");
    }
    if (load_state_from_pack(pack_a, state_a) != 0 ||
        load_state_from_pack(pack_b, state_b) != 0) {
        return fail("coredata load failed");
    }
    if (state_a.sim_digest != state_b.sim_digest) {
        return fail("sim digest mismatch");
    }
    if (ingest_state(state_a, summary_a) != 0 ||
        ingest_state(state_b, summary_b) != 0) {
        return fail("coredata ingest failed");
    }
    if (summary_a.graph_hash != summary_b.graph_hash ||
        summary_a.system_count != summary_b.system_count ||
        summary_a.body_count != summary_b.body_count ||
        summary_a.system_profile_count != summary_b.system_profile_count ||
        summary_a.site_profile_count != summary_b.site_profile_count) {
        return fail("ingest summary mismatch");
    }
    return 0;
}

static int test_identity_digest_boundaries(void) {
    dom::tools::CoredataData data;
    dom::tools::CoredataData tweaked;
    dom::tools::CoredataPack pack_base;
    dom::tools::CoredataPack pack_display;
    dom::tools::CoredataPack pack_mech;
    dom_coredata_state state_base;
    dom_coredata_state state_display;
    dom_coredata_state state_mech;

    if (load_data(fixture_path("coredata_valid"), data, true) != 0) {
        return fail("load coredata_valid failed");
    }
    if (emit_pack(data, pack_base) != 0 ||
        load_state_from_pack(pack_base, state_base) != 0) {
        return fail("base pack load failed");
    }

    tweaked = data;
    if (!tweaked.anchors.empty()) {
        tweaked.anchors[0].display_name = "Display Name Override";
    }
    if (emit_pack(tweaked, pack_display) != 0 ||
        load_state_from_pack(pack_display, state_display) != 0) {
        return fail("display tweak pack load failed");
    }
    if (state_base.sim_digest != state_display.sim_digest) {
        return fail("display name affected sim digest");
    }

    tweaked = data;
    if (!tweaked.system_profiles.empty()) {
        tweaked.system_profiles[0].navigation_instability_q16 += 1;
    }
    if (emit_pack(tweaked, pack_mech) != 0 ||
        load_state_from_pack(pack_mech, state_mech) != 0) {
        return fail("mechanics tweak pack load failed");
    }
    if (state_base.sim_digest == state_mech.sim_digest) {
        return fail("mechanics change did not affect sim digest");
    }
    return 0;
}

static void init_instance(dom::InstanceInfo &inst) {
    inst.id = "coredata_test";
    inst.world_seed = 1u;
    inst.world_size_m = 128u;
    inst.vertical_min_m = -16;
    inst.vertical_max_m = 64;
    inst.suite_version = 1u;
    inst.core_version = 1u;
    inst.last_product = "game";
    inst.last_product_version = "0.0.0";
    inst.packs.clear();
    inst.mods.clear();
}

static bool init_session(dom::DomSession &session,
                         dom::Paths &paths,
                         dom::InstanceInfo &inst,
                         const std::string &pack_root) {
    dom::SessionConfig scfg;
    scfg.platform_backend = "null";
    scfg.gfx_backend = "null";
    scfg.audio_backend = std::string();
    scfg.headless = true;
    scfg.tui = false;
    scfg.allow_missing_content = false;

    if (!dom::resolve_paths(paths, ".")) {
        return false;
    }
    if (!pack_root.empty()) {
        paths.packs = pack_root;
    }
    return session.init(paths, inst, scfg);
}

static int test_missing_pack_refusal(void) {
    dom::DomSession session;
    dom::DomGameNet net;
    dom::InstanceInfo inst;
    dom::Paths paths;
    dom_game_runtime *rt = 0;
    dom_game_runtime_init_desc desc;
    const std::string pack_root = fixture_path("missing_packs");

    init_instance(inst);
    if (!init_session(session, paths, inst, pack_root)) {
        return fail("session init failed");
    }

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_GAME_RUNTIME_INIT_DESC_VERSION;
    desc.session = &session;
    desc.net = &net;
    desc.instance = &inst;
    desc.ups = 60u;
    desc.run_id = 1ull;

    rt = dom_game_runtime_create(&desc);
    if (rt) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("runtime created despite missing pack");
    }
    if (dom_game_runtime_last_error() != DOM_GAME_RUNTIME_LAST_ERR_COREDATA_MISSING) {
        session.shutdown();
        return fail("missing pack did not raise coredata missing error");
    }
    session.shutdown();
    return 0;
}

static int test_invalid_reference_refusal(void) {
    dom::tools::CoredataData data;
    dom::tools::CoredataPack pack;
    dom_coredata_state state;
    std::string err;
    int rc = 0;

    if (load_data(fixture_path("coredata_invalid_missing_profile"), data, false) != 0) {
        return fail("load invalid fixture failed");
    }
    if (emit_pack(data, pack) != 0) {
        return fail("emit invalid pack failed");
    }

    rc = dom_coredata_load_from_bytes(pack.pack_bytes.empty() ? 0 : &pack.pack_bytes[0],
                                      pack.pack_bytes.size(),
                                      &state,
                                      &err);
    if (rc != DOM_COREDATA_MISSING_REFERENCE) {
        std::fprintf(stderr, "unexpected load rc=%d err=%s\n", rc, err.c_str());
        return fail("invalid reference did not refuse");
    }
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_coredata_ingest_determinism()) != 0) return rc;
    if ((rc = test_identity_digest_boundaries()) != 0) return rc;
    if ((rc = test_missing_pack_refusal()) != 0) return rc;
    if ((rc = test_invalid_reference_refusal()) != 0) return rc;
    std::printf("dominium coredata tests passed\n");
    return 0;
}
