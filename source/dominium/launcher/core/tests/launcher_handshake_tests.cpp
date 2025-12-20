/*
FILE: source/dominium/launcher/core/tests/launcher_handshake_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / tests
RESPONSIBILITY: Handshake TLV determinism + launcher-side refusal helpers tests.
NOTES: Runs under null services; no UI/gfx dependencies.
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "launcher_artifact_store.h"
#include "launcher_handshake.h"
#include "launcher_pack_manifest.h"
#include "launcher_sha256.h"

namespace {

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool write_file_all(const std::string& path, const std::vector<unsigned char>& bytes) {
    FILE* f = std::fopen(path.c_str(), "wb");
    size_t wrote = 0u;
    if (!f) return false;
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    return wrote == bytes.size();
}

static void remove_file_best_effort(const std::string& path) {
    (void)std::remove(path.c_str());
}

#if defined(_WIN32) || defined(_WIN64)
extern "C" int _mkdir(const char* path);
extern "C" int _rmdir(const char* path);
#else
extern "C" int mkdir(const char* path, unsigned int mode);
extern "C" int rmdir(const char* path);
#endif

static void mkdir_one_best_effort(const std::string& path) {
    if (path.empty()) return;
#if defined(_WIN32) || defined(_WIN64)
    (void)_mkdir(path.c_str());
#else
    (void)mkdir(path.c_str(), 0777u);
#endif
}

static void mkdir_p_best_effort(const std::string& path) {
    std::string p = normalize_seps(path);
    size_t i;
    if (p.empty()) return;
    for (i = 0u; i < p.size(); ++i) {
        if (p[i] == '/') {
            std::string part = p.substr(0u, i);
            if (!part.empty()) mkdir_one_best_effort(part);
        }
    }
    mkdir_one_best_effort(p);
}

static void rmdir_best_effort(const std::string& path) {
#if defined(_WIN32) || defined(_WIN64)
    (void)_rmdir(path.c_str());
#else
    (void)rmdir(path.c_str());
#endif
}

static void u64_to_hex16(u64 v, char out_hex[17]) {
    static const char* hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        out_hex[i] = hex[nib & 0xFu];
    }
    out_hex[16] = '\0';
}

static std::string bytes_to_hex_lower(const std::vector<unsigned char>& bytes) {
    static const char* hex = "0123456789abcdef";
    std::string out;
    size_t i;
    out.reserve(bytes.size() * 2u);
    for (i = 0u; i < bytes.size(); ++i) {
        unsigned v = (unsigned)bytes[i];
        out.push_back(hex[(v >> 4u) & 0xFu]);
        out.push_back(hex[v & 0xFu]);
    }
    return out;
}

static std::string make_temp_root(const launcher_services_api_v1* services, const char* prefix) {
    void* iface = 0;
    const launcher_time_api_v1* time = 0;
    char hex[17];
    u64 stamp = 0ull;
    if (services && services->query_interface && services->query_interface(LAUNCHER_IID_TIME_V1, &iface) == 0) {
        time = (const launcher_time_api_v1*)iface;
    }
    if (time && time->now_us) {
        stamp = time->now_us();
    }
    u64_to_hex16(stamp, hex);
    return std::string(prefix ? prefix : "tmp") + "_" + std::string(hex);
}

static dom::launcher_core::LauncherPackManifest make_pack_manifest(const std::string& id,
                                                                   u32 pack_type,
                                                                   const std::string& version) {
    dom::launcher_core::LauncherPackManifest pm;
    pm.pack_id = id;
    pm.pack_type = pack_type;
    pm.version = version;
    pm.phase = (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL;
    pm.explicit_order = 0;
    pm.pack_hash_bytes.assign(32u, (unsigned char)0x42u);

    pm.has_compatible_engine_range = 1u;
    pm.has_compatible_game_range = 1u;
    pm.compatible_engine_range.min_version.clear();
    pm.compatible_engine_range.max_version.clear();
    pm.compatible_game_range.min_version.clear();
    pm.compatible_game_range.max_version.clear();

    pm.declared_capabilities.clear();
    pm.sim_affecting_flags.clear();
    pm.required_packs.clear();
    pm.optional_packs.clear();
    pm.conflicts.clear();
    pm.install_tasks.clear();
    pm.verify_tasks.clear();
    pm.prelaunch_tasks.clear();
    return pm;
}

struct CreatedArtifact {
    dom::launcher_core::LauncherContentEntry entry;
    std::string hash_hex;
};

static CreatedArtifact create_pack_artifact(const std::string& state_root,
                                            const dom::launcher_core::LauncherPackManifest& pm,
                                            u32 content_type) {
    CreatedArtifact out;
    std::vector<unsigned char> payload;
    unsigned char hash_raw[dom::launcher_core::LAUNCHER_SHA256_BYTES];
    std::vector<unsigned char> hash_bytes;
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    dom::launcher_core::LauncherArtifactMetadata meta;
    std::vector<unsigned char> meta_bytes;

    out.entry = dom::launcher_core::LauncherContentEntry();
    out.hash_hex.clear();

    assert(dom::launcher_core::launcher_pack_manifest_to_tlv_bytes(pm, payload));
    std::memset(hash_raw, 0, sizeof(hash_raw));
    dom::launcher_core::launcher_sha256_bytes(payload.empty() ? (const unsigned char*)0 : &payload[0], payload.size(), hash_raw);
    hash_bytes.assign(hash_raw, hash_raw + (size_t)dom::launcher_core::LAUNCHER_SHA256_BYTES);

    assert(dom::launcher_core::launcher_artifact_store_paths(state_root, hash_bytes, dir, meta_path, payload_path));
    mkdir_p_best_effort(path_join(dir, "payload"));
    assert(write_file_all(payload_path, payload));

    meta.hash_bytes = hash_bytes;
    meta.size_bytes = (u64)payload.size();
    meta.content_type = content_type;
    meta.timestamp_us = 0ull;
    meta.verification_status = (u32)dom::launcher_core::LAUNCHER_ARTIFACT_VERIFY_VERIFIED;
    meta.source.clear();
    assert(dom::launcher_core::launcher_artifact_metadata_to_tlv_bytes(meta, meta_bytes));
    assert(write_file_all(meta_path, meta_bytes));

    out.entry.type = content_type;
    out.entry.id = pm.pack_id;
    out.entry.version = pm.version;
    out.entry.hash_bytes = hash_bytes;
    out.entry.enabled = 1u;
    out.entry.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT;
    out.hash_hex = bytes_to_hex_lower(hash_bytes);
    return out;
}

static void cleanup_artifacts_best_effort(const std::string& state_root,
                                          const std::vector<std::string>& artifact_hexes) {
    size_t i;
    for (i = 0u; i < artifact_hexes.size(); ++i) {
        const std::string dir = path_join(path_join(path_join(state_root, "artifacts"), "sha256"), artifact_hexes[i]);
        remove_file_best_effort(path_join(dir, "artifact.tlv"));
        remove_file_best_effort(path_join(path_join(dir, "payload"), dom::launcher_core::launcher_artifact_store_payload_filename()));
        rmdir_best_effort(path_join(dir, "payload"));
        rmdir_best_effort(dir);
    }
    rmdir_best_effort(path_join(path_join(state_root, "artifacts"), "sha256"));
    rmdir_best_effort(path_join(state_root, "artifacts"));
}

static void cleanup_state_root_best_effort(const std::string& state_root) {
    rmdir_best_effort(state_root);
}

static void test_serialize_parse_roundtrip_and_order_preservation() {
    dom::launcher_core::LauncherHandshake hs;
    dom::launcher_core::LauncherHandshake parsed;
    std::vector<unsigned char> a;
    std::vector<unsigned char> b;

    hs.run_id = 123ull;
    hs.instance_id = "inst_roundtrip";
    hs.instance_manifest_hash_bytes.assign(32u, (unsigned char)0xAAu);
    hs.launcher_profile_id = "baseline";
    hs.determinism_profile_id = "baseline";
    hs.selected_platform_backends.push_back("win32");
    hs.selected_platform_backends.push_back("posix"); /* intentionally unsorted */
    hs.selected_renderer_backends.push_back("soft");
    hs.selected_renderer_backends.push_back("null");
    hs.selected_ui_backend_id = "null";
    hs.pinned_engine_build_id = "engine.build";
    hs.pinned_game_build_id = "game.build";
    hs.timestamp_monotonic_us = 456ull;
    hs.has_timestamp_wall_us = 1u;
    hs.timestamp_wall_us = 789ull;

    {
        dom::launcher_core::LauncherHandshakePackEntry p;
        p.pack_id = "pack.b";
        p.version = "1.0.0";
        p.hash_bytes.assign(4u, (unsigned char)0x11u);
        p.enabled = 1u;
        p.sim_affecting_flags.push_back("z");
        p.sim_affecting_flags.push_back("a");
        p.safe_mode_flags.push_back("disable_mods");
        p.safe_mode_flags.push_back("safe_mode");
        p.offline_mode_flag = 1u;
        hs.resolved_packs.push_back(p);
    }
    {
        dom::launcher_core::LauncherHandshakePackEntry p;
        p.pack_id = "pack.a";
        p.version = "2.0.0";
        p.hash_bytes.assign(4u, (unsigned char)0x22u);
        p.enabled = 1u;
        p.offline_mode_flag = 0u;
        hs.resolved_packs.push_back(p);
    }

    assert(dom::launcher_core::launcher_handshake_to_tlv_bytes(hs, a));
    assert(dom::launcher_core::launcher_handshake_from_tlv_bytes(a.empty() ? (const unsigned char*)0 : &a[0], a.size(), parsed));
    assert(dom::launcher_core::launcher_handshake_to_tlv_bytes(parsed, b));
    assert(a == b);

    /* Ordered pack list preservation */
    assert(parsed.resolved_packs.size() == 2u);
    assert(parsed.resolved_packs[0].pack_id == "pack.b");
    assert(parsed.resolved_packs[1].pack_id == "pack.a");

    /* Stable hash across runs (fixed input). */
    {
        const u64 h = dom::launcher_core::launcher_handshake_hash64(hs);
        /* NOTE: This is a golden value for the canonical bytes of `hs` above. */
        const u64 expected = 0xd383c0743cead9ddull;
        assert(h == expected);
    }
}

static void test_refusals() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_handshake_refusal");
    std::vector<std::string> artifact_hexes;

    mkdir_p_best_effort(state_root);

    dom::launcher_core::LauncherPackManifest pm = make_pack_manifest("sim.one",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "1.0.0");
    pm.declared_capabilities.push_back("sim.affects");
    pm.sim_affecting_flags.push_back("sim.affects");

    CreatedArtifact art = create_pack_artifact(state_root, pm, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(art.hash_hex);

    dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst_hs");
    m.pinned_engine_build_id = "engine.pinned";
    m.pinned_game_build_id = "game.pinned";
    m.content_entries.clear();
    m.content_entries.push_back(art.entry);

    dom::launcher_core::LauncherHandshake hs;
    hs.run_id = 1ull;
    hs.instance_id = m.instance_id;
    hs.launcher_profile_id = "baseline";
    hs.determinism_profile_id = "baseline";
    hs.selected_platform_backends.push_back("win32");
    hs.selected_ui_backend_id = "null";
    hs.pinned_engine_build_id = m.pinned_engine_build_id;
    hs.pinned_game_build_id = m.pinned_game_build_id;
    hs.timestamp_monotonic_us = 2ull;
    hs.instance_manifest_hash_bytes.clear();
    hs.instance_manifest_hash_bytes.resize(32u, (unsigned char)0u);
    {
        std::vector<unsigned char> mt;
        unsigned char mh[dom::launcher_core::LAUNCHER_SHA256_BYTES];
        assert(dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(m, mt));
        dom::launcher_core::launcher_sha256_bytes(mt.empty() ? (const unsigned char*)0 : &mt[0], mt.size(), mh);
        hs.instance_manifest_hash_bytes.assign(mh, mh + (size_t)dom::launcher_core::LAUNCHER_SHA256_BYTES);
    }
    {
        dom::launcher_core::LauncherHandshakePackEntry pe;
        pe.pack_id = pm.pack_id;
        pe.version = pm.version;
        pe.hash_bytes = art.entry.hash_bytes;
        pe.enabled = 1u;
        pe.sim_affecting_flags = pm.sim_affecting_flags;
        pe.offline_mode_flag = 0u;
        hs.resolved_packs.push_back(pe);
    }

    /* Missing required fields */
    {
        dom::launcher_core::LauncherHandshake bad = hs;
        bad.instance_id.clear();
        std::string detail;
        u32 code = dom::launcher_core::launcher_handshake_validate(services, bad, m, state_root, &detail);
        assert(code == (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS);
    }

    /* Manifest hash mismatch */
    {
        dom::launcher_core::LauncherHandshake bad = hs;
        bad.instance_manifest_hash_bytes[0] ^= 0xFFu;
        std::string detail;
        u32 code = dom::launcher_core::launcher_handshake_validate(services, bad, m, state_root, &detail);
        assert(code == (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MANIFEST_HASH_MISMATCH);
    }

    /* Missing sim-affecting pack declarations */
    {
        dom::launcher_core::LauncherHandshake bad = hs;
        bad.resolved_packs[0].sim_affecting_flags.clear();
        std::string detail;
        u32 code = dom::launcher_core::launcher_handshake_validate(services, bad, m, state_root, &detail);
        assert(code == (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS);
    }

    /* Pack hash mismatch */
    {
        dom::launcher_core::LauncherHandshake bad = hs;
        bad.resolved_packs[0].hash_bytes[0] ^= 0xFFu;
        std::string detail;
        u32 code = dom::launcher_core::launcher_handshake_validate(services, bad, m, state_root, &detail);
        assert(code == (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_PACK_HASH_MISMATCH);
    }

    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
}

} /* namespace */

int main() {
    test_serialize_parse_roundtrip_and_order_preservation();
    test_refusals();
    std::printf("launcher_handshake_tests: OK\n");
    return 0;
}
