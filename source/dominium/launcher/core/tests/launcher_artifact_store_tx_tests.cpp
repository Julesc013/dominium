/*
FILE: source/dominium/launcher/core/tests/launcher_artifact_store_tx_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tests
RESPONSIBILITY: Artifact store + transactional install/update/rollback engine tests (null/headless; deterministic).
NOTES: No UI/gfx dependencies; uses only standard C/C++ file IO and launcher null services.
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
#include "launcher_instance_artifact_ops.h"
#include "launcher_instance_known_good.h"
#include "launcher_instance_ops.h"
#include "launcher_instance_payload_refs.h"
#include "launcher_instance_tx.h"
#include "launcher_sha256.h"
#include "launcher_tlv.h"

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

static std::string u64_hex16_string(u64 v) {
    char hex[17];
    u64_to_hex16(v, hex);
    return std::string(hex);
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

static bool audit_find_hex16(const dom::launcher_core::LauncherAuditLog& audit,
                             const std::string& needle,
                             std::string& out_hex16) {
    size_t i;
    size_t pos;
    for (i = 0u; i < audit.reasons.size(); ++i) {
        pos = audit.reasons[i].find(needle);
        if (pos == std::string::npos) continue;
        pos += needle.size();
        if (pos + 16u > audit.reasons[i].size()) continue;
        out_hex16 = audit.reasons[i].substr(pos, 16u);
        return true;
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

static void test_artifact_store_immutability_and_atomicity() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    std::string state_root = make_temp_root(services, "state_artifact_tx");
    dom::launcher_core::LauncherInstanceManifest created;
    dom::launcher_core::LauncherAuditLog a;
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_tx");
    std::vector<unsigned char> payload0;
    std::vector<unsigned char> hash0;
    std::string dir0, meta0_path, payload0_path;
    std::vector<unsigned char> meta0_before, payload0_before, meta0_after, payload0_after;

    payload0.push_back('h');
    payload0.push_back('i');

    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, payload0, hash0, dir0, meta0_path, payload0_path);
    assert(read_file_all(meta0_path, meta0_before));
    assert(read_file_all(payload0_path, payload0_before));

    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

    /* Install valid artifact */
    {
        dom::launcher_core::LauncherContentEntry e;
        dom::launcher_core::LauncherInstanceManifest updated;
        dom::launcher_core::LauncherAuditLog ia;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "mod.test";
        e.version = "1";
        e.hash_bytes = hash0;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        assert(dom::launcher_core::launcher_instance_install_artifact_to_instance(services, "inst_tx", e, state_root, updated, &ia));
        assert(updated.content_entries.size() == 1u);
    }

    assert(read_file_all(meta0_path, meta0_after));
    assert(read_file_all(payload0_path, payload0_after));
    assert(meta0_after == meta0_before);
    assert(payload0_after == payload0_before);

    /* Install corrupt artifact; must fail and leave live manifest unchanged */
    {
        std::vector<unsigned char> payload_bad;
        std::vector<unsigned char> hash_bad;
        std::string dir_bad, meta_bad_path, payload_bad_path;
        dom::launcher_core::LauncherContentEntry e;
        dom::launcher_core::LauncherInstanceManifest loaded_before;
        dom::launcher_core::LauncherInstanceManifest loaded_after;
        u64 h_before;
        dom::launcher_core::LauncherAuditLog ia;

        payload_bad.push_back('b');
        payload_bad.push_back('a');
        payload_bad.push_back('d');
        make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, payload_bad, hash_bad, dir_bad, meta_bad_path, payload_bad_path);

        /* Corrupt payload bytes after metadata is written */
        payload_bad[0] ^= 0xFFu;
        assert(write_file_all(payload_bad_path, payload_bad));

        assert(dom::launcher_core::launcher_instance_load_manifest(services, "inst_tx", state_root, loaded_before));
        h_before = dom::launcher_core::launcher_instance_manifest_hash64(loaded_before);

        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "mod.bad";
        e.version = "1";
        e.hash_bytes = hash_bad;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        {
            dom::launcher_core::LauncherInstanceManifest tmp;
            bool ok = dom::launcher_core::launcher_instance_install_artifact_to_instance(services, "inst_tx", e, state_root, tmp, &ia);
            assert(!ok);
        }

        assert(dom::launcher_core::launcher_instance_load_manifest(services, "inst_tx", state_root, loaded_after));
        assert(dom::launcher_core::launcher_instance_manifest_hash64(loaded_after) == h_before);
        assert(loaded_after.content_entries.size() == loaded_before.content_entries.size());
    }

    /* Cleanup (best-effort) */
    {
        dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, "inst_tx");
        remove_file_best_effort(ip.manifest_path);
        remove_file_best_effort(path_join(ip.instance_root, "payload_refs.tlv"));
        remove_file_best_effort(path_join(ip.instance_root, "known_good.tlv"));
        remove_file_best_effort(path_join(ip.staging_root, "transaction.tlv"));
        remove_file_best_effort(ip.staging_manifest_path);
        remove_file_best_effort(path_join(ip.staging_root, "payload_refs.tlv"));
        rmdir_best_effort(ip.staging_root);
        rmdir_best_effort(ip.previous_root);
        rmdir_best_effort(ip.logs_root);
        rmdir_best_effort(ip.cache_root);
        rmdir_best_effort(ip.content_root);
        rmdir_best_effort(ip.mods_root);
        rmdir_best_effort(ip.saves_root);
        remove_file_best_effort(ip.config_file_path);
        rmdir_best_effort(ip.config_root);
        rmdir_best_effort(ip.instance_root);
        rmdir_best_effort(path_join(state_root, "instances"));

        /* store */
        remove_file_best_effort(meta0_path);
        remove_file_best_effort(payload0_path);
        rmdir_best_effort(path_join(dir0, "payload"));
        rmdir_best_effort(dir0);
        rmdir_best_effort(path_join(path_join(state_root, "artifacts"), "sha256"));
        rmdir_best_effort(path_join(state_root, "artifacts"));

        rmdir_best_effort(state_root);
    }
}

static void test_update_policy_verify_repair_and_rollback() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    std::string state_root = make_temp_root(services, "state_policy");
    dom::launcher_core::LauncherAuditLog a;

    /* Create artifacts */
    std::vector<unsigned char> eng_payload;
    std::vector<unsigned char> mod0_payload;
    std::vector<unsigned char> mod1_payload;
    std::vector<unsigned char> bad_payload;

    std::vector<unsigned char> eng_hash;
    std::vector<unsigned char> mod0_hash;
    std::vector<unsigned char> mod1_hash;
    std::vector<unsigned char> bad_hash;

    std::string eng_dir, eng_meta, eng_file;
    std::string mod0_dir, mod0_meta, mod0_file;
    std::string mod1_dir, mod1_meta, mod1_file;
    std::string bad_dir, bad_meta, bad_file;

    eng_payload.push_back('e');
    eng_payload.push_back('0');
    mod0_payload.push_back('m');
    mod0_payload.push_back('0');
    mod1_payload.push_back('m');
    mod1_payload.push_back('1');
    bad_payload.push_back('b');
    bad_payload.push_back('0');

    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_ENGINE, eng_payload, eng_hash, eng_dir, eng_meta, eng_file);
    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, mod0_payload, mod0_hash, mod0_dir, mod0_meta, mod0_file);
    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, mod1_payload, mod1_hash, mod1_dir, mod1_meta, mod1_file);
    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, bad_payload, bad_hash, bad_dir, bad_meta, bad_file);

    /* Update policy: never */
    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_policy_never");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherContentEntry e;
        dom::launcher_core::LauncherContentEntry upd;
        dom::launcher_core::LauncherInstanceManifest out;
        dom::launcher_core::LauncherAuditLog ua;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "mod.p";
        e.version = "1";
        e.hash_bytes = mod0_hash;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_NEVER;
        desired.content_entries.push_back(e);
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

        upd = e;
        upd.version = "2";
        upd.hash_bytes = mod1_hash;
        assert(!dom::launcher_core::launcher_instance_update_artifact_in_instance(services, "inst_policy_never", upd, state_root, 1u, out, &ua));
        {
            dom::launcher_core::LauncherInstanceManifest loaded;
            assert(dom::launcher_core::launcher_instance_load_manifest(services, "inst_policy_never", state_root, loaded));
            assert(loaded.content_entries.size() == 1u);
            assert(loaded.content_entries[0].hash_bytes == mod0_hash);
        }
    }

    /* Update policy: prompt */
    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_policy_prompt");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherContentEntry e;
        dom::launcher_core::LauncherContentEntry upd;
        dom::launcher_core::LauncherInstanceManifest out;
        dom::launcher_core::LauncherAuditLog ua;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "mod.p";
        e.version = "1";
        e.hash_bytes = mod0_hash;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT;
        desired.content_entries.push_back(e);
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

        upd = e;
        upd.version = "2";
        upd.hash_bytes = mod1_hash;
        assert(!dom::launcher_core::launcher_instance_update_artifact_in_instance(services, "inst_policy_prompt", upd, state_root, 0u, out, &ua));
        assert(dom::launcher_core::launcher_instance_update_artifact_in_instance(services, "inst_policy_prompt", upd, state_root, 1u, out, &ua));
        assert(out.content_entries.size() == 1u);
        assert(out.content_entries[0].hash_bytes == mod1_hash);
    }

    /* Update policy: auto */
    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_policy_auto");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherContentEntry e;
        dom::launcher_core::LauncherContentEntry upd;
        dom::launcher_core::LauncherInstanceManifest out;
        dom::launcher_core::LauncherAuditLog ua;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "mod.p";
        e.version = "1";
        e.hash_bytes = mod0_hash;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        desired.content_entries.push_back(e);
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

        upd = e;
        upd.version = "2";
        upd.hash_bytes = mod1_hash;
        assert(dom::launcher_core::launcher_instance_update_artifact_in_instance(services, "inst_policy_auto", upd, state_root, 0u, out, &ua));
        assert(out.content_entries.size() == 1u);
        assert(out.content_entries[0].hash_bytes == mod1_hash);
    }

    /* Verify/repair and rollback */
    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_verify");
        dom::launcher_core::LauncherInstanceManifest created;
        dom::launcher_core::LauncherContentEntry engine;
        dom::launcher_core::LauncherContentEntry bad_mod;
        dom::launcher_core::LauncherInstanceManifest out;
        dom::launcher_core::LauncherAuditLog va;

        /* Engine artifact is required. */
        engine.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_ENGINE;
        engine.id = "engine.core";
        engine.version = "1";
        engine.hash_bytes = eng_hash;
        engine.enabled = 1u;
        engine.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;

        bad_mod.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        bad_mod.id = "mod.missing";
        bad_mod.version = "1";
        bad_mod.enabled = 1u;
        bad_mod.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        bad_mod.hash_bytes = bad_hash;

        /* Break artifact referenced by bad_mod by corrupting payload. */
        {
            std::vector<unsigned char> corrupt;
            assert(read_file_all(bad_file, corrupt));
            corrupt[0] ^= 0xFFu;
            assert(write_file_all(bad_file, corrupt));
        }

        desired.content_entries.push_back(engine);
        desired.content_entries.push_back(bad_mod);
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));

        assert(!dom::launcher_core::launcher_instance_verify_or_repair(services, "inst_verify", state_root, 0u, out, &va));

        assert(dom::launcher_core::launcher_instance_verify_or_repair(services, "inst_verify", state_root, 1u, out, &va));
        assert(out.known_good == 1u);
        assert(out.content_entries.size() == 2u);
        assert(out.content_entries[1].enabled == 0u);

        /* known_good pointer + snapshot should exist */
        {
            dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, "inst_verify");
            std::vector<unsigned char> kg_bytes;
            dom::launcher_core::LauncherInstanceKnownGoodPointer kg;
            assert(read_file_all(path_join(ip.instance_root, "known_good.tlv"), kg_bytes));
            assert(dom::launcher_core::launcher_instance_known_good_from_tlv_bytes(&kg_bytes[0], kg_bytes.size(), kg));
            assert(!kg.previous_dir.empty());
            assert(file_exists(path_join(path_join(ip.previous_root, kg.previous_dir), "manifest.tlv")));
        }

        /* Mutate instance by installing a valid mod, then rollback to known good */
        {
            dom::launcher_core::LauncherContentEntry ok_mod;
            dom::launcher_core::LauncherInstanceManifest tmp;
            dom::launcher_core::LauncherAuditLog ia;
            std::string txid_hex;
            ok_mod.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
            ok_mod.id = "mod.ok";
            ok_mod.version = "1";
            ok_mod.hash_bytes = mod0_hash;
            ok_mod.enabled = 1u;
            ok_mod.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
            assert(dom::launcher_core::launcher_instance_install_artifact_to_instance(services, "inst_verify", ok_mod, state_root, tmp, &ia));

            /* parse txid from audit for linkage */
            assert(audit_find_hex16(ia, "txid=0x", txid_hex));
            u64 source_tx = 0ull;
            {
                /* parse hex16 to u64 deterministically */
                size_t i;
                for (i = 0u; i < 16u; ++i) {
                    char c = txid_hex[i];
                    unsigned v = 0u;
                    if (c >= '0' && c <= '9') v = (unsigned)(c - '0');
                    else if (c >= 'a' && c <= 'f') v = (unsigned)(10u + (unsigned)(c - 'a'));
                    else if (c >= 'A' && c <= 'F') v = (unsigned)(10u + (unsigned)(c - 'A'));
                    source_tx = (u64)((source_tx << 4u) | (u64)v);
                }
            }

            assert(dom::launcher_core::launcher_instance_rollback_to_known_good(services, "inst_verify", state_root,
                                                                               std::string("test_cause"),
                                                                               source_tx,
                                                                               tmp, &ia));
            assert(tmp.content_entries.size() == 2u);
            assert(tmp.content_entries[1].id == "mod.missing");
            assert(tmp.content_entries[1].enabled == 0u);
        }
    }

    /* Cleanup (best-effort; minimal) */
    {
        rmdir_best_effort(state_root);
    }
}

static void test_crash_recovery_modes() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    std::string state_root = make_temp_root(services, "state_crash");
    dom::launcher_core::LauncherAuditLog a;

    /* Create valid artifact */
    std::vector<unsigned char> payload;
    std::vector<unsigned char> hash;
    std::string dir, meta_path, payload_path;
    payload.push_back('x');
    payload.push_back('y');
    make_store_artifact(state_root, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD, payload, hash, dir, meta_path, payload_path);

    /* Create instance */
    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_crash");
        dom::launcher_core::LauncherInstanceManifest created;
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &a));
    }

    dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, "inst_crash");

    /* Crash during staging: tx marker present + partial staged manifest */
    {
        dom::launcher_core::LauncherInstanceTx tx;
        dom::launcher_core::LauncherAuditLog ta;
        std::vector<unsigned char> one;
        one.push_back(0xAAu);
        assert(dom::launcher_core::launcher_instance_tx_prepare(services, "inst_crash", state_root,
                                                                (u32)dom::launcher_core::LAUNCHER_INSTANCE_TX_OP_INSTALL, tx, &ta));
        mkdir_p_best_effort(ip.staging_root);
        assert(write_file_all(ip.staging_manifest_path, one));
        assert(dom::launcher_core::launcher_instance_tx_recover_staging(services, "inst_crash", state_root, &ta));
        assert(!file_exists(ip.staging_manifest_path));
        assert(!file_exists(path_join(ip.staging_root, "transaction.tlv")));
    }

    /* Crash during verify: tx marker indicates VERIFY + partial payload_refs */
    {
        dom::launcher_core::TlvWriter w;
        std::vector<unsigned char> tx_bytes;
        std::vector<unsigned char> junk;
        dom::launcher_core::LauncherAuditLog ta;
        u64 txid = 0x1111ull;
        w.add_u32(dom::launcher_core::LAUNCHER_TLV_TAG_SCHEMA_VERSION, dom::launcher_core::LAUNCHER_INSTANCE_TX_TLV_VERSION);
        w.add_u64(dom::launcher_core::LAUNCHER_INSTANCE_TX_TLV_TAG_TX_ID, txid);
        w.add_string(dom::launcher_core::LAUNCHER_INSTANCE_TX_TLV_TAG_INSTANCE_ID, "inst_crash");
        w.add_u32(dom::launcher_core::LAUNCHER_INSTANCE_TX_TLV_TAG_OP_TYPE, (u32)dom::launcher_core::LAUNCHER_INSTANCE_TX_OP_INSTALL);
        w.add_u32(dom::launcher_core::LAUNCHER_INSTANCE_TX_TLV_TAG_PHASE, (u32)dom::launcher_core::LAUNCHER_INSTANCE_TX_PHASE_VERIFY);
        w.add_u64(dom::launcher_core::LAUNCHER_INSTANCE_TX_TLV_TAG_BEFORE_MANIFEST_HASH64, 0ull);
        w.add_u64(dom::launcher_core::LAUNCHER_INSTANCE_TX_TLV_TAG_AFTER_MANIFEST_HASH64, 0ull);
        tx_bytes = w.bytes();
        junk.push_back(0xBBu);
        mkdir_p_best_effort(ip.staging_root);
        assert(write_file_all(path_join(ip.staging_root, "transaction.tlv"), tx_bytes));
        assert(write_file_all(path_join(ip.staging_root, "payload_refs.tlv"), junk));
        assert(dom::launcher_core::launcher_instance_tx_recover_staging(services, "inst_crash", state_root, &ta));
        assert(!file_exists(path_join(ip.staging_root, "payload_refs.tlv")));
        assert(!file_exists(path_join(ip.staging_root, "transaction.tlv")));
    }

    /* Crash before commit: staged manifest + payload_refs via tx engine */
    {
        dom::launcher_core::LauncherInstanceTx tx;
        dom::launcher_core::LauncherAuditLog ta;
        dom::launcher_core::LauncherContentEntry e;
        dom::launcher_core::LauncherInstanceManifest after;
        assert(dom::launcher_core::launcher_instance_tx_prepare(services, "inst_crash", state_root,
                                                                (u32)dom::launcher_core::LAUNCHER_INSTANCE_TX_OP_INSTALL, tx, &ta));
        after = tx.before_manifest;
        after.schema_version = dom::launcher_core::LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
        after.previous_manifest_hash64 = tx.before_manifest_hash64;
        after.known_good = 0u;
        after.last_verified_timestamp_us = 0ull;
        e.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
        e.id = "mod.ok";
        e.version = "1";
        e.hash_bytes = hash;
        e.enabled = 1u;
        e.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
        after.content_entries.push_back(e);
        tx.after_manifest = after;
        assert(dom::launcher_core::launcher_instance_tx_stage(services, tx, &ta));
        assert(dom::launcher_core::launcher_instance_tx_verify(services, tx, &ta));
        assert(file_exists(ip.staging_manifest_path));
        assert(file_exists(path_join(ip.staging_root, "payload_refs.tlv")));
        assert(dom::launcher_core::launcher_instance_tx_recover_staging(services, "inst_crash", state_root, &ta));
        assert(!file_exists(ip.staging_manifest_path));
        assert(!file_exists(path_join(ip.staging_root, "payload_refs.tlv")));
        assert(!file_exists(path_join(ip.staging_root, "transaction.tlv")));
    }

    /* Cleanup (best-effort) */
    {
        remove_file_best_effort(meta_path);
        remove_file_best_effort(payload_path);
        rmdir_best_effort(path_join(dir, "payload"));
        rmdir_best_effort(dir);
        rmdir_best_effort(path_join(path_join(state_root, "artifacts"), "sha256"));
        rmdir_best_effort(path_join(state_root, "artifacts"));

        remove_file_best_effort(ip.manifest_path);
        rmdir_best_effort(ip.previous_root);
        rmdir_best_effort(ip.logs_root);
        rmdir_best_effort(ip.cache_root);
        rmdir_best_effort(ip.content_root);
        rmdir_best_effort(ip.mods_root);
        rmdir_best_effort(ip.saves_root);
        remove_file_best_effort(ip.config_file_path);
        rmdir_best_effort(ip.config_root);
        rmdir_best_effort(ip.staging_root);
        rmdir_best_effort(ip.instance_root);
        rmdir_best_effort(path_join(state_root, "instances"));
        rmdir_best_effort(state_root);
    }
}

} /* namespace */

int main() {
    test_artifact_store_immutability_and_atomicity();
    test_update_policy_verify_repair_and_rollback();
    test_crash_recovery_modes();
    std::printf("launcher_artifact_store_tx_tests: OK\n");
    return 0;
}
