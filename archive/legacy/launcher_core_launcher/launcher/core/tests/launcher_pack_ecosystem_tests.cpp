/*
FILE: source/dominium/launcher/core/tests/launcher_pack_ecosystem_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / tests
RESPONSIBILITY: Pack/mod/runtime ecosystem tests (dependency resolution, conflicts, deterministic load order, policies, sim safety).
NOTES: Runs under null services; no UI/gfx dependencies.
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "launcher_artifact_store.h"
#include "launcher_audit.h"
#include "launcher_core_api.h"
#include "launcher_instance.h"
#include "launcher_instance_ops.h"
#include "launcher_pack_manifest.h"
#include "launcher_pack_ops.h"
#include "launcher_pack_resolver.h"
#include "launcher_sha256.h"

namespace {

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

static bool audit_find_kv_hex16(const dom::launcher_core::LauncherAuditLog& audit,
                                const std::string& key,
                                std::string& out_hex16) {
    const std::string needle = key + "=0x";
    size_t i;
    for (i = 0u; i < audit.reasons.size(); ++i) {
        const std::string& s = audit.reasons[i];
        size_t pos = s.find(needle);
        if (pos == std::string::npos) continue;
        pos += needle.size();
        if (pos + 16u > s.size()) continue;
        out_hex16 = s.substr(pos, 16u);
        return true;
    }
    return false;
}

struct CreatedArtifact {
    dom::launcher_core::LauncherContentEntry entry;
    std::string hash_hex;
};

static dom::launcher_core::LauncherPackManifest make_pack_manifest(const std::string& id,
                                                                   u32 pack_type,
                                                                   const std::string& version,
                                                                   u32 phase,
                                                                   i32 explicit_order) {
    dom::launcher_core::LauncherPackManifest pm;
    pm.pack_id = id;
    pm.pack_type = pack_type;
    pm.version = version;
    pm.phase = phase;
    pm.explicit_order = explicit_order;
    pm.declared_capabilities.clear();
    pm.sim_affecting_flags.clear();
    pm.required_packs.clear();
    pm.optional_packs.clear();
    pm.conflicts.clear();
    pm.install_tasks.clear();
    pm.verify_tasks.clear();
    pm.prelaunch_tasks.clear();

    /* Required field: pack_hash_bytes (opaque in this revision). */
    pm.pack_hash_bytes.assign(32u, (unsigned char)0x42u);

    /* Required field: compatible ranges present (may be unbounded). */
    pm.has_compatible_engine_range = 1u;
    pm.has_compatible_game_range = 1u;
    pm.compatible_engine_range.min_version.clear();
    pm.compatible_engine_range.max_version.clear();
    pm.compatible_game_range.min_version.clear();
    pm.compatible_game_range.max_version.clear();

    return pm;
}

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

static void cleanup_instance_best_effort(const std::string& state_root,
                                         const std::string& instance_id,
                                         const std::vector<std::string>& prev_dirs) {
    dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
    size_t i;

    remove_file_best_effort(ip.manifest_path);
    remove_file_best_effort(path_join(ip.instance_root, "payload_refs.tlv"));
    remove_file_best_effort(path_join(ip.instance_root, "known_good.tlv"));

    /* staging */
    remove_file_best_effort(ip.staging_manifest_path);
    remove_file_best_effort(path_join(ip.staging_root, "payload_refs.tlv"));
    remove_file_best_effort(path_join(ip.staging_root, "transaction.tlv"));
    rmdir_best_effort(ip.staging_root);

    /* previous snapshots created by tx engine */
    for (i = 0u; i < prev_dirs.size(); ++i) {
        const std::string prev_root = path_join(ip.previous_root, prev_dirs[i]);
        remove_file_best_effort(path_join(prev_root, "manifest.tlv"));
        remove_file_best_effort(path_join(prev_root, "payload_refs.tlv"));
        remove_file_best_effort(path_join(prev_root, "known_good.tlv"));
        rmdir_best_effort(prev_root);
    }
    rmdir_best_effort(ip.previous_root);

    /* config */
    remove_file_best_effort(ip.config_file_path);
    rmdir_best_effort(ip.config_root);

    rmdir_best_effort(ip.logs_root);
    rmdir_best_effort(ip.cache_root);
    rmdir_best_effort(ip.content_root);
    rmdir_best_effort(ip.mods_root);
    rmdir_best_effort(ip.saves_root);

    rmdir_best_effort(ip.instance_root);
    rmdir_best_effort(ip.instances_root);
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
    rmdir_best_effort(path_join(state_root, "instances"));
    rmdir_best_effort(state_root);
}

static void collect_prev_dir_from_audit(const dom::launcher_core::LauncherAuditLog& audit,
                                        std::vector<std::string>& io_prev_dirs) {
    std::string txid_hex;
    std::string before_hex;
    if (!audit_find_kv_hex16(audit, "txid", txid_hex)) return;
    if (!audit_find_kv_hex16(audit, "before_manifest_hash64", before_hex)) return;
    io_prev_dirs.push_back(before_hex + "_" + txid_hex);
}

static void test_dependency_resolution_and_ordering() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_pack_resolve");
    std::vector<std::string> artifact_hexes;
    std::vector<std::string> prev_dirs;

    mkdir_p_best_effort(state_root);

    dom::launcher_core::LauncherPackManifest dep = make_pack_manifest("dep.ok",
                                                                      (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                      "1.0.0",
                                                                      (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                      0);
    CreatedArtifact dep_art = create_pack_artifact(state_root, dep, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(dep_art.hash_hex);

    dom::launcher_core::LauncherPackManifest need = make_pack_manifest("needs.dep",
                                                                       (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                       "1.0.0",
                                                                       (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                       0);
    {
        dom::launcher_core::LauncherPackDependency d;
        d.pack_id = "dep.ok";
        d.version_range.min_version = "1.0.0";
        d.version_range.max_version = "1.0.0";
        need.required_packs.push_back(d);
    }
    CreatedArtifact need_art = create_pack_artifact(state_root, need, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(need_art.hash_hex);

    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_dep");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherAuditLog a;
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));
    }

    {
        dom::launcher_core::LauncherInstanceManifest outm;
        dom::launcher_core::LauncherAuditLog a1;
        std::string err;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_dep", dep_art.entry, state_root, outm, &a1, &err));
        collect_prev_dir_from_audit(a1, prev_dirs);
        dom::launcher_core::LauncherAuditLog a2;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_dep", need_art.entry, state_root, outm, &a2, &err));
        collect_prev_dir_from_audit(a2, prev_dirs);

        std::vector<dom::launcher_core::LauncherResolvedPack> order;
        std::string rerr;
        assert(dom::launcher_core::launcher_pack_resolve_enabled(services, outm, state_root, order, &rerr));
        assert(order.size() == 2u);
        assert(order[0].pack_id == "dep.ok");
        assert(order[1].pack_id == "needs.dep");
    }

    cleanup_instance_best_effort(state_root, "inst_dep", prev_dirs);
    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
}

static void test_conflict_detection() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_pack_conflict");
    std::vector<std::string> artifact_hexes;
    std::vector<std::string> prev_dirs;

    mkdir_p_best_effort(state_root);

    dom::launcher_core::LauncherPackManifest a = make_pack_manifest("conflict.a",
                                                                    (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                    "1.0.0",
                                                                    (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                    0);
    dom::launcher_core::LauncherPackManifest b = make_pack_manifest("conflict.b",
                                                                    (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                    "1.0.0",
                                                                    (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                    0);
    {
        dom::launcher_core::LauncherPackDependency c;
        c.pack_id = "conflict.b";
        c.version_range.min_version = "1.0.0";
        c.version_range.max_version = "1.0.0";
        a.conflicts.push_back(c);
    }

    CreatedArtifact a_art = create_pack_artifact(state_root, a, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    CreatedArtifact b_art = create_pack_artifact(state_root, b, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(a_art.hash_hex);
    artifact_hexes.push_back(b_art.hash_hex);

    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_conf");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherAuditLog a0;
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a0));
    }

    {
        dom::launcher_core::LauncherInstanceManifest outm;
        std::string err;
        dom::launcher_core::LauncherAuditLog a1;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_conf", a_art.entry, state_root, outm, &a1, &err));
        collect_prev_dir_from_audit(a1, prev_dirs);

        dom::launcher_core::LauncherAuditLog a2;
        bool ok = dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_conf", b_art.entry, state_root, outm, &a2, &err);
        assert(!ok);
        assert(err.find("conflict_violation") != std::string::npos);
    }

    cleanup_instance_best_effort(state_root, "inst_conf", prev_dirs);
    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
}

static void test_deterministic_load_order_and_overrides() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_pack_order");
    std::vector<std::string> artifact_hexes;
    std::vector<std::string> prev_dirs;

    mkdir_p_best_effort(state_root);

    dom::launcher_core::LauncherPackManifest pa = make_pack_manifest("pack.a",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "1.0.0",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                     5);
    dom::launcher_core::LauncherPackManifest pb = make_pack_manifest("pack.b",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "1.0.0",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                     1);
    dom::launcher_core::LauncherPackManifest pc = make_pack_manifest("pack.c",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "1.0.0",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_EARLY,
                                                                     100);
    dom::launcher_core::LauncherPackManifest pd = make_pack_manifest("pack.d",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "1.0.0",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_LATE,
                                                                     -1);

    CreatedArtifact a_art = create_pack_artifact(state_root, pa, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    CreatedArtifact b_art = create_pack_artifact(state_root, pb, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    CreatedArtifact c_art = create_pack_artifact(state_root, pc, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    CreatedArtifact d_art = create_pack_artifact(state_root, pd, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(a_art.hash_hex);
    artifact_hexes.push_back(b_art.hash_hex);
    artifact_hexes.push_back(c_art.hash_hex);
    artifact_hexes.push_back(d_art.hash_hex);

    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_order");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherAuditLog a0;
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a0));
    }

    {
        dom::launcher_core::LauncherInstanceManifest outm;
        std::string err;

        dom::launcher_core::LauncherAuditLog a1;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_order", d_art.entry, state_root, outm, &a1, &err));
        collect_prev_dir_from_audit(a1, prev_dirs);
        dom::launcher_core::LauncherAuditLog a2;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_order", a_art.entry, state_root, outm, &a2, &err));
        collect_prev_dir_from_audit(a2, prev_dirs);
        dom::launcher_core::LauncherAuditLog a3;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_order", c_art.entry, state_root, outm, &a3, &err));
        collect_prev_dir_from_audit(a3, prev_dirs);
        dom::launcher_core::LauncherAuditLog a4;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_order", b_art.entry, state_root, outm, &a4, &err));
        collect_prev_dir_from_audit(a4, prev_dirs);

        std::vector<dom::launcher_core::LauncherResolvedPack> order;
        std::string rerr;
        assert(dom::launcher_core::launcher_pack_resolve_enabled(services, outm, state_root, order, &rerr));
        assert(order.size() == 4u);
        assert(order[0].pack_id == "pack.c");
        assert(order[1].pack_id == "pack.b");
        assert(order[2].pack_id == "pack.a");
        assert(order[3].pack_id == "pack.d");

        dom::launcher_core::LauncherAuditLog a5;
        assert(dom::launcher_core::launcher_pack_set_order_override_in_instance(services,
                                                                                "inst_order",
                                                                                (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK,
                                                                                "pack.a",
                                                                                1u,
                                                                                0,
                                                                                state_root,
                                                                                outm,
                                                                                &a5,
                                                                                &err));
        collect_prev_dir_from_audit(a5, prev_dirs);

        assert(dom::launcher_core::launcher_pack_resolve_enabled(services, outm, state_root, order, &rerr));
        assert(order.size() == 4u);
        assert(order[0].pack_id == "pack.c");
        assert(order[1].pack_id == "pack.a");
        assert(order[2].pack_id == "pack.b");
        assert(order[3].pack_id == "pack.d");
    }

    cleanup_instance_best_effort(state_root, "inst_order", prev_dirs);
    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
}

static void test_enable_disable_semantics() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_pack_enable");
    std::vector<std::string> artifact_hexes;
    std::vector<std::string> prev_dirs;

    mkdir_p_best_effort(state_root);

    dom::launcher_core::LauncherPackManifest dep = make_pack_manifest("dep.base",
                                                                      (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                      "1.0.0",
                                                                      (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                      0);
    dom::launcher_core::LauncherPackManifest need = make_pack_manifest("needs.base",
                                                                       (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                       "1.0.0",
                                                                       (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                       0);
    {
        dom::launcher_core::LauncherPackDependency d;
        d.pack_id = "dep.base";
        d.version_range.min_version = "1.0.0";
        d.version_range.max_version = "1.0.0";
        need.required_packs.push_back(d);
    }

    CreatedArtifact dep_art = create_pack_artifact(state_root, dep, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    CreatedArtifact need_art = create_pack_artifact(state_root, need, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(dep_art.hash_hex);
    artifact_hexes.push_back(need_art.hash_hex);

    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_enable");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherAuditLog a0;
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a0));
    }

    {
        dom::launcher_core::LauncherInstanceManifest outm;
        std::string err;
        dom::launcher_core::LauncherAuditLog a1;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_enable", dep_art.entry, state_root, outm, &a1, &err));
        collect_prev_dir_from_audit(a1, prev_dirs);
        dom::launcher_core::LauncherAuditLog a2;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_enable", need_art.entry, state_root, outm, &a2, &err));
        collect_prev_dir_from_audit(a2, prev_dirs);

        dom::launcher_core::LauncherAuditLog a3;
        bool ok = dom::launcher_core::launcher_pack_set_enabled_in_instance(services,
                                                                            "inst_enable",
                                                                            (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK,
                                                                            "dep.base",
                                                                            0u,
                                                                            state_root,
                                                                            outm,
                                                                            &a3,
                                                                            &err);
        assert(!ok);
        assert(err.find("missing_required_pack") != std::string::npos);

        dom::launcher_core::LauncherAuditLog a4;
        assert(dom::launcher_core::launcher_pack_set_enabled_in_instance(services,
                                                                         "inst_enable",
                                                                         (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK,
                                                                         "needs.base",
                                                                         0u,
                                                                         state_root,
                                                                         outm,
                                                                         &a4,
                                                                         &err));
        collect_prev_dir_from_audit(a4, prev_dirs);

        dom::launcher_core::LauncherAuditLog a5;
        assert(dom::launcher_core::launcher_pack_set_enabled_in_instance(services,
                                                                         "inst_enable",
                                                                         (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK,
                                                                         "dep.base",
                                                                         0u,
                                                                         state_root,
                                                                         outm,
                                                                         &a5,
                                                                         &err));
        collect_prev_dir_from_audit(a5, prev_dirs);
    }

    cleanup_instance_best_effort(state_root, "inst_enable", prev_dirs);
    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
}

static void test_update_policy_enforcement() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_pack_update_policy");
    std::vector<std::string> artifact_hexes;
    std::vector<std::string> prev_dirs;

    mkdir_p_best_effort(state_root);

    dom::launcher_core::LauncherPackManifest v1 = make_pack_manifest("upd.never",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "1.0.0",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                     0);
    dom::launcher_core::LauncherPackManifest v2 = make_pack_manifest("upd.never",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "2.0.0",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                     0);
    CreatedArtifact a1 = create_pack_artifact(state_root, v1, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    CreatedArtifact a2 = create_pack_artifact(state_root, v2, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(a1.hash_hex);
    artifact_hexes.push_back(a2.hash_hex);

    dom::launcher_core::LauncherPackManifest p1 = make_pack_manifest("upd.prompt",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "1.0.0",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                     0);
    dom::launcher_core::LauncherPackManifest p2 = make_pack_manifest("upd.prompt",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                     "2.0.0",
                                                                     (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                     0);
    CreatedArtifact b1 = create_pack_artifact(state_root, p1, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    CreatedArtifact b2 = create_pack_artifact(state_root, p2, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(b1.hash_hex);
    artifact_hexes.push_back(b2.hash_hex);

    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_upd");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherAuditLog a0;
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a0));
    }

    {
        dom::launcher_core::LauncherInstanceManifest outm;
        std::string err;

        a1.entry.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_NEVER;
        dom::launcher_core::LauncherAuditLog a;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_upd", a1.entry, state_root, outm, &a, &err));
        collect_prev_dir_from_audit(a, prev_dirs);

        dom::launcher_core::LauncherAuditLog au;
        bool ok = dom::launcher_core::launcher_pack_update_pack_in_instance(services, "inst_upd", a2.entry, state_root, 1u, outm, &au, &err);
        assert(!ok);
        assert(err == "update_policy_never");

        b1.entry.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT;
        dom::launcher_core::LauncherAuditLog b;
        assert(dom::launcher_core::launcher_pack_install_pack_to_instance(services, "inst_upd", b1.entry, state_root, outm, &b, &err));
        collect_prev_dir_from_audit(b, prev_dirs);

        dom::launcher_core::LauncherAuditLog bu0;
        ok = dom::launcher_core::launcher_pack_update_pack_in_instance(services, "inst_upd", b2.entry, state_root, 0u, outm, &bu0, &err);
        assert(!ok);
        assert(err == "update_policy_prompt_requires_override");

        dom::launcher_core::LauncherAuditLog bu1;
        ok = dom::launcher_core::launcher_pack_update_pack_in_instance(services, "inst_upd", b2.entry, state_root, 1u, outm, &bu1, &err);
        assert(ok);
        collect_prev_dir_from_audit(bu1, prev_dirs);
    }

    cleanup_instance_best_effort(state_root, "inst_upd", prev_dirs);
    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
}

static void test_sim_affecting_refusal() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_pack_sim");
    std::vector<std::string> artifact_hexes;

    mkdir_p_best_effort(state_root);

    dom::launcher_core::LauncherPackManifest dep = make_pack_manifest("sim.dep",
                                                                      (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                      "1.0.0",
                                                                      (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                      0);
    dep.declared_capabilities.push_back("sim.affects");
    dep.sim_affecting_flags.push_back("sim.affects");

    dom::launcher_core::LauncherPackManifest main = make_pack_manifest("sim.main",
                                                                       (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_CONTENT,
                                                                       "1.0.0",
                                                                       (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL,
                                                                       0);
    main.declared_capabilities.push_back("sim.affects");
    main.sim_affecting_flags.push_back("sim.affects");
    {
        dom::launcher_core::LauncherPackDependency d;
        d.pack_id = "sim.dep";
        d.version_range.min_version = "1.0.0";
        d.version_range.max_version = "1.0.0";
        main.required_packs.push_back(d);
    }

    CreatedArtifact dep_art = create_pack_artifact(state_root, dep, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    CreatedArtifact main_art = create_pack_artifact(state_root, main, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK);
    artifact_hexes.push_back(dep_art.hash_hex);
    artifact_hexes.push_back(main_art.hash_hex);

    {
        dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst_sim");
        m.content_entries.clear();
        m.content_entries.push_back(main_art.entry);
        std::string err;
        bool ok = dom::launcher_core::launcher_pack_validate_simulation_safety(services, m, state_root, &err);
        assert(!ok);
        assert(err.find("missing_required_pack") != std::string::npos);
    }

    {
        dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst_sim2");
        dom::launcher_core::LauncherContentEntry bad = dep_art.entry;
        bad.version = "0.0.0";
        m.content_entries.clear();
        m.content_entries.push_back(bad);
        std::string err;
        bool ok = dom::launcher_core::launcher_pack_validate_simulation_safety(services, m, state_root, &err);
        assert(!ok);
        assert(err.find("pack_version_mismatch") != std::string::npos);
    }

    cleanup_artifacts_best_effort(state_root, artifact_hexes);
    cleanup_state_root_best_effort(state_root);
}

} /* namespace */

int main() {
    test_dependency_resolution_and_ordering();
    test_conflict_detection();
    test_deterministic_load_order_and_overrides();
    test_enable_disable_semantics();
    test_update_policy_enforcement();
    test_sim_affecting_refusal();
    std::printf("launcher_pack_ecosystem_tests: OK\n");
    return 0;
}
