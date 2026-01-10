/*
FILE: source/tests/dom_tool_handshake_validation_test.cpp
MODULE: Dominium Tests
PURPOSE: Ensure tool runtime refuses mismatched SIM_CAPS handshakes.
*/
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "dom_tool_runtime.h"
#include "dom_caps.h"
#include "dominium/core_tlv.h"
#include "runtime/dom_game_handshake.h"

#if defined(_WIN32) || defined(_WIN64)
#include <direct.h>
#else
#include <sys/stat.h>
#include <sys/types.h>
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static bool mkdir_one(const std::string &path) {
#if defined(_WIN32) || defined(_WIN64)
    return _mkdir(path.c_str()) == 0 || errno == EEXIST;
#else
    return mkdir(path.c_str(), 0755) == 0 || errno == EEXIST;
#endif
}

static void rmdir_one(const std::string &path) {
#if defined(_WIN32) || defined(_WIN64)
    _rmdir(path.c_str());
#else
    rmdir(path.c_str());
#endif
}

static bool write_bytes(const std::string &path, const std::vector<unsigned char> &bytes) {
    FILE *f = std::fopen(path.c_str(), "wb");
    size_t wrote = 0u;
    if (!f) {
        return false;
    }
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    return wrote == bytes.size();
}

static bool set_env_var(const char *key, const std::string &value) {
#if defined(_WIN32) || defined(_WIN64)
    return _putenv_s(key, value.c_str()) == 0;
#else
    return setenv(key, value.c_str(), 1) == 0;
#endif
}

int main() {
    const std::string run_root = "tmp_tool_run";
    const std::string home_root = "tmp_tool_home";
    const std::string hs_path = run_root + "/handshake.tlv";
    dom::DomSimCaps sim_caps;
    std::vector<unsigned char> sim_caps_tlv;
    std::vector<unsigned char> hs_bytes;
    dom::tools::DomToolRuntime rt;
    std::string err;

    if (!mkdir_one(run_root) || !mkdir_one(home_root)) {
        return fail("mkdir_failed");
    }
    if (!set_env_var("DOMINIUM_RUN_ROOT", run_root) ||
        !set_env_var("DOMINIUM_HOME", home_root)) {
        return fail("set_env_failed");
    }

    dom::dom_sim_caps_init_default(sim_caps);
    sim_caps.sim_flags += 1u; /* force mismatch */
    if (!dom::dom_sim_caps_to_tlv(sim_caps, sim_caps_tlv)) {
        return fail("sim_caps_tlv_failed");
    }

    {
        unsigned char manifest_hash[8];
        std::memset(manifest_hash, 0, sizeof(manifest_hash));
        dom::core_tlv::TlvWriter w;
        w.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_GAME_HANDSHAKE_TLV_VERSION);
        w.add_u64(DOM_GAME_HANDSHAKE_TLV_TAG_RUN_ID, 1ull);
        w.add_string(DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_ID, "inst1");
        w.add_bytes(DOM_GAME_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH,
                    manifest_hash,
                    (u32)sizeof(manifest_hash));
        w.add_container(DOM_GAME_HANDSHAKE_TLV_TAG_SIM_CAPS, sim_caps_tlv);
        hs_bytes = w.bytes();
    }

    if (hs_bytes.empty() || !write_bytes(hs_path, hs_bytes)) {
        return fail("handshake_write_failed");
    }

    if (!dom::tools::tool_runtime_init(rt,
                                       "validator",
                                       "handshake.tlv",
                                       dom::DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED,
                                       false,
                                       &err)) {
        return fail("tool_runtime_init_failed");
    }
    if (dom::tools::tool_runtime_validate_identity(rt, &err)) {
        return fail("expected_sim_caps_mismatch");
    }
    if (rt.last_refusal != dom::tools::DOM_TOOL_REFUSAL_SIM_CAPS_MISMATCH) {
        return fail("refusal_code_unexpected");
    }

    std::remove(hs_path.c_str());
    rmdir_one(run_root);
    rmdir_one(home_root);
    (void)set_env_var("DOMINIUM_RUN_ROOT", "");
    (void)set_env_var("DOMINIUM_HOME", "");

    std::printf("dom_tool_handshake_validation_test: OK\n");
    return 0;
}
