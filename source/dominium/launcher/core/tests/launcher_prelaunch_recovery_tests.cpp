/*
FILE: source/dominium/launcher/core/tests/launcher_prelaunch_recovery_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tests
RESPONSIBILITY: Pre-launch configuration, safe-mode, and recovery path tests (deterministic; null services).
NOTES: No UI/gfx dependencies; uses only standard C/C++ file IO and launcher null services.
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "launcher_audit.h"
#include "launcher_artifact_store.h"
#include "launcher_core_api.h"
#include "launcher_instance.h"
#include "launcher_instance_artifact_ops.h"
#include "launcher_instance_config.h"
#include "launcher_instance_known_good.h"
#include "launcher_instance_launch_history.h"
#include "launcher_instance_ops.h"
#include "launcher_launch_attempt.h"
#include "launcher_pack_manifest.h"
#include "launcher_prelaunch.h"
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

static bool file_exists(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fclose(f);
    return true;
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

static bool read_file_all(const std::string& path, std::vector<unsigned char>& out_bytes) {
    FILE* f;
    long sz;
    size_t got;
    out_bytes.clear();
    f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    if (std::fseek(f, 0L, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0L) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0L, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    out_bytes.resize((size_t)sz);
    got = 0u;
    if (sz > 0L) {
        got = std::fread(&out_bytes[0], 1u, (size_t)sz, f);
    }
    std::fclose(f);
    return got == (size_t)sz;
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

static void remove_file_best_effort(const std::string& path) {
    (void)std::remove(path.c_str());
}

static void rmdir_best_effort(const std::string& path) {
#if defined(_WIN32) || defined(_WIN64)
    (void)_rmdir(path.c_str());
#else
    (void)rmdir(path.c_str());
#endif
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
    return std::string(prefix) + "_" + std::string(hex);
}

static bool audit_has_substr(const dom::launcher_core::LauncherAuditLog& audit, const std::string& needle) {
    size_t i;
    for (i = 0u; i < audit.reasons.size(); ++i) {
        if (audit.reasons[i].find(needle) != std::string::npos) {
            return true;
        }
    }
    return false;
}

static std::vector<unsigned char> make_pack_manifest_payload(const std::string& pack_id,
                                                             u32 pack_type,
                                                             const std::string& version) {
    dom::launcher_core::LauncherPackManifest pm;
    std::vector<unsigned char> bytes;
    std::string err;

    pm.pack_id = pack_id;
    pm.pack_type = pack_type;
    pm.version = version;
    pm.pack_hash_bytes.clear();
    pm.pack_hash_bytes.push_back(0x01u);
    pm.pack_hash_bytes.push_back(0x02u);
    pm.has_compatible_engine_range = 1u;
    pm.has_compatible_game_range = 1u;
    pm.compatible_engine_range.min_version.clear();
    pm.compatible_engine_range.max_version.clear();
    pm.compatible_game_range.min_version.clear();
    pm.compatible_game_range.max_version.clear();
    pm.phase = (u32)dom::launcher_core::LAUNCHER_PACK_PHASE_NORMAL;
    pm.explicit_order = 0;

    assert(dom::launcher_core::launcher_pack_manifest_validate(pm, &err));
    assert(dom::launcher_core::launcher_pack_manifest_to_tlv_bytes(pm, bytes));
    return bytes;
}

static bool manifest_has_entry(const dom::launcher_core::LauncherInstanceManifest& m,
                               u32 type,
                               const std::string& id,
                               u32* out_enabled) {
    size_t i;
    for (i = 0u; i < m.content_entries.size(); ++i) {
        const dom::launcher_core::LauncherContentEntry& e = m.content_entries[i];
        if (e.type == type && e.id == id) {
            if (out_enabled) {
                *out_enabled = e.enabled ? 1u : 0u;
            }
            return true;
        }
    }
    return false;
}

static void make_store_artifact(const std::string& state_root,
                                u32 content_type,
                                const std::vector<unsigned char>& payload_bytes,
                                std::vector<unsigned char>& out_hash_bytes,
                                std::string& out_artifact_dir,
                                std::string& out_meta_path,
                                std::string& out_payload_path) {
    unsigned char h[dom::launcher_core::LAUNCHER_SHA256_BYTES];
    dom::launcher_core::LauncherArtifactMetadata meta;
    std::vector<unsigned char> meta_bytes;
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    std::string payload_dir;

    dom::launcher_core::launcher_sha256_bytes(payload_bytes.empty() ? (const unsigned char*)0 : &payload_bytes[0],
                                              payload_bytes.size(),
                                              h);
    out_hash_bytes.assign(h, h + dom::launcher_core::LAUNCHER_SHA256_BYTES);

    assert(dom::launcher_core::launcher_artifact_store_paths(state_root, out_hash_bytes, dir, meta_path, payload_path));
    payload_dir = path_join(dir, "payload");
    mkdir_p_best_effort(payload_dir);

    assert(write_file_all(payload_path, payload_bytes));

    meta.hash_bytes = out_hash_bytes;
    meta.size_bytes = (u64)payload_bytes.size();
    meta.content_type = content_type;
    meta.timestamp_us = 0ull;
    meta.verification_status = (u32)dom::launcher_core::LAUNCHER_ARTIFACT_VERIFY_VERIFIED;
    meta.source = "test";
    assert(dom::launcher_core::launcher_artifact_metadata_to_tlv_bytes(meta, meta_bytes));
    assert(write_file_all(meta_path, meta_bytes));

    out_artifact_dir = dir;
    out_meta_path = meta_path;
    out_payload_path = payload_path;
}

static void cleanup_artifact_best_effort(const std::string& artifact_dir,
                                        const std::string& meta_path,
                                        const std::string& payload_path) {
    remove_file_best_effort(meta_path);
    remove_file_best_effort(payload_path);
    rmdir_best_effort(path_join(artifact_dir, "payload"));
    rmdir_best_effort(artifact_dir);
}

static void cleanup_instance_best_effort(const std::string& state_root,
                                         const std::string& instance_id) {
    dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
    remove_file_best_effort(ip.manifest_path);
    remove_file_best_effort(path_join(ip.instance_root, "known_good.tlv"));
    remove_file_best_effort(path_join(ip.instance_root, "payload_refs.tlv"));
    remove_file_best_effort(ip.config_file_path);
    remove_file_best_effort(path_join(ip.logs_root, "launch_history.tlv"));
    remove_file_best_effort(path_join(ip.logs_root, "prelaunch_writable_probe.tmp"));

    rmdir_best_effort(ip.staging_root);
    rmdir_best_effort(ip.logs_root);
    rmdir_best_effort(ip.cache_root);
    rmdir_best_effort(ip.content_root);
    rmdir_best_effort(ip.mods_root);
    rmdir_best_effort(ip.saves_root);
    rmdir_best_effort(ip.config_root);

    /* Previous root can contain unknown tx dirs; best-effort only. */
    rmdir_best_effort(ip.previous_root);
    rmdir_best_effort(ip.instance_root);
    rmdir_best_effort(path_join(state_root, "instances"));
    rmdir_best_effort(state_root);
}

static void test_config_resolution_determinism() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    std::string state_root = make_temp_root(services, "state_prelaunch_cfg_det");
    const std::string instance_id = "inst_cfg_det";
    dom::launcher_core::LauncherAuditLog a;
    dom::launcher_core::LauncherInstanceManifest created;
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(instance_id);

    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

    dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
    dom::launcher_core::LauncherInstanceConfig cfg = dom::launcher_core::launcher_instance_config_make_default(instance_id);
    cfg.gfx_backend = "dx11";
    cfg.renderer_api = "auto";
    cfg.window_mode = (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_WINDOWED;
    cfg.window_width = 1280u;
    cfg.window_height = 720u;
    cfg.window_dpi = 96u;
    cfg.window_monitor = 1u;
    cfg.audio_device_id = "default";
    cfg.input_backend = "raw";
    cfg.allow_network = 1u;
    cfg.debug_flags = 3u;
    cfg.auto_recovery_failure_threshold = 4u;
    cfg.launch_history_max_entries = 7u;
    {
        dom::launcher_core::LauncherDomainOverride d0;
        d0.domain_key = "domain.a";
        d0.enabled = 1u;
        dom::launcher_core::LauncherDomainOverride d1;
        d1.domain_key = "domain.b";
        d1.enabled = 0u;
        cfg.domain_overrides.push_back(d0);
        cfg.domain_overrides.push_back(d1);
    }
    assert(dom::launcher_core::launcher_instance_config_store(services, ip, cfg));

    dom::launcher_core::LauncherLaunchOverrides o;
    o.has_gfx_backend = 1u;
    o.gfx_backend = "gl2";
    o.has_debug_flags = 1u;
    o.debug_flags = 9u;

    dom::launcher_core::LauncherPrelaunchPlan p1, p2;
    dom::launcher_core::LauncherAuditLog a1, a2;
    std::string e1, e2;

    assert(dom::launcher_core::launcher_prelaunch_build_plan(services, (const dom::launcher_core::LauncherProfile*)0,
                                                             instance_id, state_root, o, p1, &a1, &e1));
    assert(dom::launcher_core::launcher_prelaunch_build_plan(services, (const dom::launcher_core::LauncherProfile*)0,
                                                             instance_id, state_root, o, p2, &a2, &e2));

    assert(p1.validation.ok == 1u);
    assert(p2.validation.ok == 1u);
    assert(p1.base_manifest_hash64 == p2.base_manifest_hash64);
    assert(p1.resolved_config_hash64 == p2.resolved_config_hash64);

    assert(p1.resolved.safe_mode == 0u);
    assert(p1.resolved.gfx_backend == "gl2");
    assert(p1.resolved.debug_flags == 9u);
    assert(p1.resolved.domain_overrides.size() == 2u);
    assert(p1.resolved.domain_overrides[0].domain_key == "domain.a");
    assert(p1.resolved.domain_overrides[1].domain_key == "domain.b");

    cleanup_instance_best_effort(state_root, instance_id);
}

static void test_override_isolation() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    std::string state_root = make_temp_root(services, "state_prelaunch_override_iso");
    const std::string instance_id = "inst_override_iso";
    dom::launcher_core::LauncherAuditLog a;
    dom::launcher_core::LauncherInstanceManifest created;
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(instance_id);
    std::vector<unsigned char> manifest_before;
    std::vector<unsigned char> manifest_after_cfg;
    std::vector<unsigned char> manifest_after_plan;

    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

    dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
    assert(read_file_all(ip.manifest_path, manifest_before));

    /* Persist overrides in config/config.tlv and ensure manifest is untouched. */
    {
        dom::launcher_core::LauncherInstanceConfig cfg = dom::launcher_core::launcher_instance_config_make_default(instance_id);
        cfg.gfx_backend = "dx9";
        cfg.allow_network = 0u;
        assert(dom::launcher_core::launcher_instance_config_store(services, ip, cfg));
    }
    assert(read_file_all(ip.manifest_path, manifest_after_cfg));
    assert(manifest_before == manifest_after_cfg);

    /* Ephemeral overrides should not mutate the manifest either. */
    {
        dom::launcher_core::LauncherLaunchOverrides o;
        o.has_gfx_backend = 1u;
        o.gfx_backend = "vk1";
        dom::launcher_core::LauncherPrelaunchPlan plan;
        dom::launcher_core::LauncherAuditLog pa;
        std::string err;
        assert(dom::launcher_core::launcher_prelaunch_build_plan(services, (const dom::launcher_core::LauncherProfile*)0,
                                                                 instance_id, state_root, o, plan, &pa, &err));
        assert(plan.resolved.gfx_backend == "vk1");
    }
    assert(read_file_all(ip.manifest_path, manifest_after_plan));
    assert(manifest_before == manifest_after_plan);

    cleanup_instance_best_effort(state_root, instance_id);
}

static void test_safe_mode_known_good_selection_and_overlay() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    std::string state_root = make_temp_root(services, "state_prelaunch_safe_mode");
    const std::string instance_id = "inst_safe_mode";
    dom::launcher_core::LauncherAuditLog a;
    dom::launcher_core::LauncherInstanceManifest created;
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(instance_id);
    dom::launcher_core::LauncherInstanceManifest updated;

    std::vector<unsigned char> payload_mod;
    std::vector<unsigned char> payload_pack;
    std::vector<unsigned char> hash_mod;
    std::vector<unsigned char> hash_pack;
    std::string dir_mod, meta_mod, pay_mod;
    std::string dir_pack, meta_pack, pay_pack;

    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

    payload_mod.push_back('m');
    payload_mod.push_back('1');
    payload_pack.push_back('p');
    payload_pack.push_back('1');

    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, payload_mod, hash_mod, dir_mod, meta_mod, pay_mod);
    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK, payload_pack, hash_pack, dir_pack, meta_pack, pay_pack);

    {
        dom::launcher_core::LauncherContentEntry e;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "modA";
        e.version = "1";
        e.hash_bytes = hash_mod;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        assert(dom::launcher_core::launcher_instance_install_artifact_to_instance(services, instance_id, e, state_root, updated, &a));
    }
    {
        dom::launcher_core::LauncherContentEntry e;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK;
        e.id = "packA";
        e.version = "1";
        e.hash_bytes = hash_pack;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        assert(dom::launcher_core::launcher_instance_install_artifact_to_instance(services, instance_id, e, state_root, updated, &a));
    }

    /* Create a known-good snapshot. */
    assert(dom::launcher_core::launcher_instance_verify_or_repair(services, instance_id, state_root, 0u, updated, &a));

    /* Diverge live manifest after known-good by adding another mod. */
    {
        std::vector<unsigned char> payload_mod2;
        std::vector<unsigned char> hash_mod2;
        std::string dir_mod2, meta_mod2, pay_mod2;
        payload_mod2.push_back('m');
        payload_mod2.push_back('2');
        make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, payload_mod2, hash_mod2, dir_mod2, meta_mod2, pay_mod2);

        dom::launcher_core::LauncherContentEntry e;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "modB";
        e.version = "1";
        e.hash_bytes = hash_mod2;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        assert(dom::launcher_core::launcher_instance_install_artifact_to_instance(services, instance_id, e, state_root, updated, &a));

        cleanup_artifact_best_effort(dir_mod2, meta_mod2, pay_mod2);
    }

    dom::launcher_core::LauncherLaunchOverrides o;
    o.request_safe_mode = 1u;
    o.safe_mode_allow_network = 0u;

    dom::launcher_core::LauncherPrelaunchPlan plan;
    dom::launcher_core::LauncherAuditLog pa;
    std::string err;
    assert(dom::launcher_core::launcher_prelaunch_build_plan(services, (const dom::launcher_core::LauncherProfile*)0,
                                                             instance_id, state_root, o, plan, &pa, &err));

    assert(plan.validation.ok == 1u);
    assert(plan.resolved.safe_mode == 1u);
    assert(plan.resolved.allow_network == 0u);
    assert(plan.resolved.gfx_backend == "null");
    assert(plan.resolved.used_known_good_manifest == 1u);
    assert(!plan.resolved.known_good_previous_dir.empty());

    {
        u32 en = 0u;
        assert(manifest_has_entry(plan.base_manifest, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, "modA", &en));
        assert(en == 1u);
        assert(manifest_has_entry(plan.base_manifest, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK, "packA", &en));
        assert(en == 1u);
        assert(!manifest_has_entry(plan.base_manifest, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, "modB", (u32*)0));

        assert(manifest_has_entry(plan.effective_manifest, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, "modA", &en));
        assert(en == 0u);
        assert(manifest_has_entry(plan.effective_manifest, (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK, "packA", &en));
        assert(en == 0u);
    }

    /* Live manifest remains diverged (safe mode does not write back). */
    {
        dom::launcher_core::LauncherInstanceManifest live;
        assert(dom::launcher_core::launcher_instance_load_manifest(services, instance_id, state_root, live));
        assert(manifest_has_entry(live, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, "modB", (u32*)0));
    }

    cleanup_artifact_best_effort(dir_mod, meta_mod, pay_mod);
    cleanup_artifact_best_effort(dir_pack, meta_pack, pay_pack);
    cleanup_instance_best_effort(state_root, instance_id);
}

static void test_auto_recovery_suggestion_logic() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    std::string state_root = make_temp_root(services, "state_prelaunch_recovery");
    const std::string instance_id = "inst_recovery";
    dom::launcher_core::LauncherAuditLog a;
    dom::launcher_core::LauncherInstanceManifest created;
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(instance_id);

    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

    dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
    {
        dom::launcher_core::LauncherInstanceConfig cfg = dom::launcher_core::launcher_instance_config_make_default(instance_id);
        cfg.auto_recovery_failure_threshold = 2u;
        assert(dom::launcher_core::launcher_instance_config_store(services, ip, cfg));
    }

    /* Two consecutive failures trigger auto safe mode. */
    {
        dom::launcher_core::LauncherInstanceLaunchHistory hist = dom::launcher_core::launcher_instance_launch_history_make_default(instance_id, 10u);
        dom::launcher_core::LauncherInstanceLaunchAttempt a0;
        dom::launcher_core::LauncherInstanceLaunchAttempt a1;
        a0.timestamp_us = 1ull;
        a0.outcome = (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_CRASH;
        a1.timestamp_us = 2ull;
        a1.outcome = (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_REFUSAL;
        dom::launcher_core::launcher_instance_launch_history_append(hist, a0);
        dom::launcher_core::launcher_instance_launch_history_append(hist, a1);
        assert(dom::launcher_core::launcher_instance_launch_history_store(services, ip, hist));

        dom::launcher_core::LauncherLaunchOverrides req;
        dom::launcher_core::LauncherPrelaunchPlan plan;
        dom::launcher_core::LauncherRecoverySuggestion rec;
        dom::launcher_core::LauncherAuditLog la;
        std::string err;
        assert(dom::launcher_core::launcher_launch_prepare_attempt(services, (const dom::launcher_core::LauncherProfile*)0,
                                                                   instance_id, state_root, req, plan, rec, &la, &err));
        assert(rec.threshold == 2u);
        assert(rec.consecutive_failures == 2u);
        assert(rec.suggest_safe_mode == 1u);
        assert(rec.suggest_rollback == 1u);
        assert(rec.auto_entered_safe_mode == 1u);
        assert(plan.resolved.safe_mode == 1u);
        assert(audit_has_substr(la, "launch_recovery;"));
    }

    /* One failure does not trigger auto safe mode. */
    {
        dom::launcher_core::LauncherInstanceLaunchHistory hist = dom::launcher_core::launcher_instance_launch_history_make_default(instance_id, 10u);
        dom::launcher_core::LauncherInstanceLaunchAttempt a0;
        a0.timestamp_us = 3ull;
        a0.outcome = (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_CRASH;
        dom::launcher_core::launcher_instance_launch_history_append(hist, a0);
        assert(dom::launcher_core::launcher_instance_launch_history_store(services, ip, hist));

        dom::launcher_core::LauncherLaunchOverrides req;
        dom::launcher_core::LauncherPrelaunchPlan plan;
        dom::launcher_core::LauncherRecoverySuggestion rec;
        dom::launcher_core::LauncherAuditLog la;
        std::string err;
        assert(dom::launcher_core::launcher_launch_prepare_attempt(services, (const dom::launcher_core::LauncherProfile*)0,
                                                                   instance_id, state_root, req, plan, rec, &la, &err));
        assert(rec.threshold == 2u);
        assert(rec.consecutive_failures == 1u);
        assert(rec.auto_entered_safe_mode == 0u);
        assert(plan.resolved.safe_mode == 0u);
    }

    cleanup_instance_best_effort(state_root, instance_id);
}

static void test_rollback_to_known_good_after_successful_launch() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    std::string state_root = make_temp_root(services, "state_prelaunch_rollback");
    const std::string instance_id = "inst_rollback";
    dom::launcher_core::LauncherAuditLog a;
    dom::launcher_core::LauncherInstanceManifest created;
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(instance_id);
    dom::launcher_core::LauncherInstanceManifest updated;

    std::vector<unsigned char> payload_mod1;
    std::vector<unsigned char> payload_mod2;
    std::vector<unsigned char> hash_mod1;
    std::vector<unsigned char> hash_mod2;
    std::string dir_mod1, meta_mod1, pay_mod1;
    std::string dir_mod2, meta_mod2, pay_mod2;

    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

    payload_mod1 = make_pack_manifest_payload("mod1", (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_MOD, "1");
    payload_mod2 = make_pack_manifest_payload("mod2", (u32)dom::launcher_core::LAUNCHER_PACK_TYPE_MOD, "1");

    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, payload_mod1, hash_mod1, dir_mod1, meta_mod1, pay_mod1);
    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, payload_mod2, hash_mod2, dir_mod2, meta_mod2, pay_mod2);

    {
        dom::launcher_core::LauncherContentEntry e;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "mod1";
        e.version = "1";
        e.hash_bytes = hash_mod1;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        assert(dom::launcher_core::launcher_instance_install_artifact_to_instance(services, instance_id, e, state_root, updated, &a));
    }

    /* Simulate a successful launch; should update last-known-good via verify (writes known_good.tlv + snapshot). */
    {
        dom::launcher_core::LauncherLaunchOverrides req;
        dom::launcher_core::LauncherPrelaunchPlan plan;
        dom::launcher_core::LauncherRecoverySuggestion rec;
        dom::launcher_core::LauncherAuditLog la;
        std::string err;
        assert(dom::launcher_core::launcher_launch_prepare_attempt(services, (const dom::launcher_core::LauncherProfile*)0,
                                                                   instance_id, state_root, req, plan, rec, &la, &err));
        assert(plan.validation.ok == 1u);
        assert(dom::launcher_core::launcher_launch_finalize_attempt(services,
                                                                    plan,
                                                                    (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_SUCCESS,
                                                                    0,
                                                                    std::string(),
                                                                    0u,
                                                                    &la,
                                                                    &err));
        assert(file_exists(path_join(dom::launcher_core::launcher_instance_paths_make(state_root, instance_id).instance_root, "known_good.tlv")));
        assert(audit_has_substr(la, "last_known_good;result=ok"));
    }

    /* Diverge instance by installing another mod, then rollback to known-good. */
    {
        dom::launcher_core::LauncherContentEntry e;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "mod2";
        e.version = "1";
        e.hash_bytes = hash_mod2;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        assert(dom::launcher_core::launcher_instance_install_artifact_to_instance(services, instance_id, e, state_root, updated, &a));
    }

    {
        dom::launcher_core::LauncherInstanceManifest restored;
        dom::launcher_core::LauncherAuditLog ra;
        assert(dom::launcher_core::launcher_instance_rollback_to_known_good(services, instance_id, state_root,
                                                                            "test", 0ull, restored, &ra));
        assert(audit_has_substr(ra, "rollback"));
        assert(manifest_has_entry(restored, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, "mod1", (u32*)0));
        assert(!manifest_has_entry(restored, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, "mod2", (u32*)0));
        assert(restored.known_good == 1u);
    }

    cleanup_artifact_best_effort(dir_mod1, meta_mod1, pay_mod1);
    cleanup_artifact_best_effort(dir_mod2, meta_mod2, pay_mod2);
    cleanup_instance_best_effort(state_root, instance_id);
}

} /* namespace */

int main() {
    test_config_resolution_determinism();
    test_override_isolation();
    test_safe_mode_known_good_selection_and_overlay();
    test_auto_recovery_suggestion_logic();
    test_rollback_to_known_good_after_successful_launch();
    std::printf("launcher_prelaunch_recovery_tests: OK\n");
    return 0;
}
