/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance_artifact_ops.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_artifact_ops
RESPONSIBILITY: Implements install/update/remove/verify/repair/rollback operations on instances via transaction engine (no in-place mutation).
*/

#include "launcher_instance_artifact_ops.h"

#include <cstdio>
#include <cstring>
#include <vector>

#include "launcher_audit.h"
#include "launcher_artifact_store.h"
#include "launcher_instance_known_good.h"
#include "launcher_instance_ops.h"
#include "launcher_instance_tx.h"
#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

static const launcher_fs_api_v1* get_fs(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_FS_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_fs_api_v1*)iface;
}

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') {
            out[i] = '/';
        }
    }
    return out;
}

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) {
        return bb;
    }
    if (bb.empty()) {
        return aa;
    }
    if (is_sep(aa[aa.size() - 1u])) {
        return aa + bb;
    }
    return aa + "/" + bb;
}

#if defined(_WIN32) || defined(_WIN64)
extern "C" int _mkdir(const char* path);
#else
extern "C" int mkdir(const char* path, unsigned int mode);
#endif

static bool mkdir_one_best_effort(const std::string& path) {
    if (path.empty()) {
        return false;
    }
    if (path == "." || path == "./") {
        return true;
    }
    if (path.size() == 2u && path[1] == ':') {
        return true;
    }
    if (path == "/") {
        return true;
    }
#if defined(_WIN32) || defined(_WIN64)
    return _mkdir(path.c_str()) == 0;
#else
    return mkdir(path.c_str(), 0777u) == 0;
#endif
}

static bool mkdir_p_best_effort(const std::string& path) {
    std::string p = normalize_seps(path);
    size_t i;

    if (p.empty()) {
        return false;
    }

    for (i = 0u; i < p.size(); ++i) {
        if (p[i] == '/') {
            std::string part = p.substr(0u, i);
            if (!part.empty()) {
                (void)mkdir_one_best_effort(part);
            }
        }
    }
    (void)mkdir_one_best_effort(p);
    return true;
}

static bool fs_write_all(const launcher_fs_api_v1* fs,
                         const std::string& path,
                         const std::vector<unsigned char>& bytes) {
    void* fh;
    size_t wrote;
    if (!fs || !fs->file_open || !fs->file_write || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "wb");
    if (!fh) {
        return false;
    }
    wrote = 0u;
    if (!bytes.empty()) {
        wrote = fs->file_write(fh, &bytes[0], bytes.size());
    }
    (void)fs->file_close(fh);
    return wrote == bytes.size();
}

static bool fs_read_all(const launcher_fs_api_v1* fs,
                        const std::string& path,
                        std::vector<unsigned char>& out_bytes) {
    void* fh;
    long sz;
    size_t got;

    out_bytes.clear();
    if (!fs || !fs->file_open || !fs->file_read || !fs->file_seek || !fs->file_tell || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }
    if (fs->file_seek(fh, 0L, SEEK_END) != 0) {
        (void)fs->file_close(fh);
        return false;
    }
    sz = fs->file_tell(fh);
    if (sz < 0L) {
        (void)fs->file_close(fh);
        return false;
    }
    if (fs->file_seek(fh, 0L, SEEK_SET) != 0) {
        (void)fs->file_close(fh);
        return false;
    }

    out_bytes.resize((size_t)sz);
    got = 0u;
    if (sz > 0L) {
        got = fs->file_read(fh, &out_bytes[0], (size_t)sz);
    }
    (void)fs->file_close(fh);
    return got == (size_t)sz;
}

static void audit_reason(LauncherAuditLog* audit, const std::string& r) {
    if (!audit) {
        return;
    }
    audit->reasons.push_back(r);
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

static std::string u64_hex16_string(u64 v) {
    char hex[17];
    u64_to_hex16(v, hex);
    return std::string(hex);
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

static void audit_tx_entry_list(LauncherAuditLog* audit,
                                u64 tx_id,
                                const std::string& side,
                                const LauncherInstanceManifest& m) {
    size_t i;
    for (i = 0u; i < m.content_entries.size(); ++i) {
        const LauncherContentEntry& e = m.content_entries[i];
        std::string line;
        line.reserve(256u);
        line += "instance_tx_artifact;";
        line += "txid=0x";
        line += u64_hex16_string(tx_id);
        line += ";side=";
        line += side;
        line += ";idx=";
        line += u64_hex16_string((u64)i);
        line += ";type=";
        line += u64_hex16_string((u64)e.type);
        line += ";enabled=";
        line += u64_hex16_string((u64)e.enabled);
        line += ";update_policy=";
        line += u64_hex16_string((u64)e.update_policy);
        line += ";id=";
        line += e.id;
        line += ";version=";
        line += e.version;
        line += ";hash_hex=";
        line += e.hash_bytes.empty() ? std::string("<empty>") : bytes_to_hex_lower(e.hash_bytes);
        audit_reason(audit, line);
    }
}

static void audit_tx_summary(LauncherAuditLog* audit,
                             const LauncherInstanceTx& tx,
                             const std::string& op,
                             const std::string& result,
                             const std::string& code,
                             const std::string& extra_kv) {
    std::string line;
    line.reserve(256u);
    line += "instance_tx_op;";
    line += "txid=0x";
    line += u64_hex16_string(tx.tx_id);
    line += ";instance_id=";
    line += tx.instance_id.empty() ? std::string("<empty>") : tx.instance_id;
    line += ";op=";
    line += op;
    line += ";result=";
    line += result;
    line += ";code=";
    line += code;
    line += ";before_manifest_hash64=0x";
    line += u64_hex16_string(tx.before_manifest_hash64);
    line += ";after_manifest_hash64=0x";
    line += u64_hex16_string(tx.after_manifest_hash64);
    if (!extra_kv.empty()) {
        line += ";";
        line += extra_kv;
    }
    audit_reason(audit, line);
}

static bool find_entry_index(const LauncherInstanceManifest& m,
                             u32 type,
                             const std::string& id,
                             size_t& out_index) {
    size_t i;
    for (i = 0u; i < m.content_entries.size(); ++i) {
        if (m.content_entries[i].type == type && m.content_entries[i].id == id) {
            out_index = i;
            return true;
        }
    }
    return false;
}

static bool is_required_type(u32 t) {
    return t == (u32)LAUNCHER_CONTENT_ENGINE || t == (u32)LAUNCHER_CONTENT_GAME || t == (u32)LAUNCHER_CONTENT_RUNTIME;
}

static bool preflight_verify_for_repair(const launcher_services_api_v1* services,
                                        const std::string& state_root,
                                        const LauncherInstanceManifest& before,
                                        u32 repair_mode,
                                        LauncherInstanceManifest& out_after,
                                        std::string& out_code) {
    LauncherInstanceManifest after = before;
    size_t i;

    out_code.clear();
    for (i = 0u; i < after.content_entries.size(); ++i) {
        LauncherContentEntry& e = after.content_entries[i];
        LauncherArtifactMetadata meta;
        bool ok;

        if (e.enabled == 0u) {
            continue;
        }
        if (e.hash_bytes.empty()) {
            if (repair_mode) {
                if (is_required_type(e.type)) {
                    out_code = "required_missing_hash";
                    return false;
                }
                e.enabled = 0u;
                continue;
            }
            out_code = "missing_hash";
            return false;
        }

        ok = launcher_artifact_store_verify(services, state_root, e.hash_bytes, e.type, meta);
        if (!ok) {
            if (repair_mode) {
                if (is_required_type(e.type)) {
                    out_code = "required_missing_or_corrupt";
                    return false;
                }
                e.enabled = 0u;
                continue;
            }
            out_code = "missing_or_corrupt";
            return false;
        }
    }

    out_after = after;
    out_code = "ok";
    return true;
}

static bool write_known_good_staging(const launcher_services_api_v1* services,
                                     const LauncherInstancePaths& paths,
                                     const LauncherInstanceTx& tx,
                                     const std::vector<unsigned char>& staged_payload_refs_bytes,
                                     LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstanceKnownGoodPointer kg;
    std::vector<unsigned char> kg_bytes;
    std::vector<unsigned char> manifest_bytes;
    std::string snapshot_dir_name;
    std::string snapshot_root;

    if (!fs) {
        return false;
    }

    snapshot_dir_name = std::string("known_good_") + u64_hex16_string(tx.after_manifest_hash64) + "_" + u64_hex16_string(tx.tx_id);

    kg.schema_version = LAUNCHER_INSTANCE_KNOWN_GOOD_TLV_VERSION;
    kg.instance_id = tx.instance_id;
    kg.previous_dir = snapshot_dir_name;
    kg.manifest_hash64 = tx.after_manifest_hash64;
    kg.timestamp_us = tx.tx_id;

    if (!launcher_instance_known_good_to_tlv_bytes(kg, kg_bytes)) {
        return false;
    }

    snapshot_root = path_join(paths.staging_root, "known_good_snapshot");
    (void)mkdir_p_best_effort(snapshot_root);

    if (!launcher_instance_manifest_to_tlv_bytes(tx.after_manifest, manifest_bytes)) {
        return false;
    }

    if (!fs_write_all(fs, path_join(snapshot_root, "payload_refs.tlv"), staged_payload_refs_bytes)) {
        return false;
    }
    if (!fs_write_all(fs, path_join(snapshot_root, "manifest.tlv"), manifest_bytes)) {
        return false;
    }
    if (!fs_write_all(fs, path_join(paths.staging_root, "known_good.tlv"), kg_bytes)) {
        return false;
    }

    audit_reason(audit,
                 std::string("instance_known_good;staged=1;instance_id=") + tx.instance_id +
                     ";txid=0x" + u64_hex16_string(tx.tx_id) +
                     ";manifest_hash64=0x" + u64_hex16_string(tx.after_manifest_hash64) +
                     ";previous_dir=" + snapshot_dir_name);
    return true;
}

} /* namespace */

bool launcher_instance_install_artifact_to_instance(const launcher_services_api_v1* services,
                                                    const std::string& instance_id,
                                                    const LauncherContentEntry& artifact_entry,
                                                    const std::string& state_root_override,
                                                    LauncherInstanceManifest& out_updated_manifest,
                                                    LauncherAuditLog* audit) {
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    size_t existing_index = 0u;

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);

    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_INSTALL, tx, audit)) {
        return false;
    }

    if (artifact_entry.id.empty() || artifact_entry.type == (u32)LAUNCHER_CONTENT_UNKNOWN || artifact_entry.hash_bytes.empty()) {
        audit_tx_summary(audit, tx, "install", "fail", "bad_artifact_entry", "");
        return false;
    }
    if (find_entry_index(tx.before_manifest, artifact_entry.type, artifact_entry.id, existing_index)) {
        audit_tx_summary(audit, tx, "install", "fail", "already_installed", "");
        return false;
    }

    after = tx.before_manifest;
    after.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    after.previous_manifest_hash64 = tx.before_manifest_hash64;
    after.known_good = 0u;
    after.last_verified_timestamp_us = 0ull;
    after.content_entries.push_back(artifact_entry);

    tx.after_manifest = after;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(after);

    audit_tx_summary(audit, tx, "install", "start", "start", "");
    audit_tx_entry_list(audit, tx.tx_id, "before", tx.before_manifest);
    audit_tx_entry_list(audit, tx.tx_id, "after", tx.after_manifest);

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        audit_tx_summary(audit, tx, "install", "fail", "stage", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        audit_tx_summary(audit, tx, "install", "fail", "verify", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        audit_tx_summary(audit, tx, "install", "fail", "commit", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_tx_summary(audit, tx, "install", "ok", "ok", "");
    return true;
}

bool launcher_instance_update_artifact_in_instance(const launcher_services_api_v1* services,
                                                   const std::string& instance_id,
                                                   const LauncherContentEntry& new_entry,
                                                   const std::string& state_root_override,
                                                   u32 override_prompt,
                                                   LauncherInstanceManifest& out_updated_manifest,
                                                   LauncherAuditLog* audit) {
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    size_t idx = 0u;
    u32 policy = 0u;

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);

    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_UPDATE, tx, audit)) {
        return false;
    }

    if (new_entry.id.empty() || new_entry.type == (u32)LAUNCHER_CONTENT_UNKNOWN || new_entry.hash_bytes.empty()) {
        audit_tx_summary(audit, tx, "update", "fail", "bad_artifact_entry", "");
        return false;
    }
    if (!find_entry_index(tx.before_manifest, new_entry.type, new_entry.id, idx)) {
        audit_tx_summary(audit, tx, "update", "fail", "missing_entry", "");
        return false;
    }

    policy = tx.before_manifest.content_entries[idx].update_policy;
    if (policy == (u32)LAUNCHER_UPDATE_NEVER) {
        audit_tx_summary(audit, tx, "update", "fail", "update_policy_never", "");
        return false;
    }
    if (policy == (u32)LAUNCHER_UPDATE_PROMPT && !override_prompt) {
        audit_tx_summary(audit, tx, "update", "fail", "update_policy_prompt_requires_override", "");
        return false;
    }

    after = tx.before_manifest;
    after.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    after.previous_manifest_hash64 = tx.before_manifest_hash64;
    after.known_good = 0u;
    after.last_verified_timestamp_us = 0ull;

    after.content_entries[idx].version = new_entry.version;
    after.content_entries[idx].hash_bytes = new_entry.hash_bytes;

    tx.after_manifest = after;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(after);

    audit_tx_summary(audit, tx, "update", "start", "start", std::string("override_prompt=") + (override_prompt ? "1" : "0"));
    audit_tx_entry_list(audit, tx.tx_id, "before", tx.before_manifest);
    audit_tx_entry_list(audit, tx.tx_id, "after", tx.after_manifest);

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        audit_tx_summary(audit, tx, "update", "fail", "stage", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        audit_tx_summary(audit, tx, "update", "fail", "verify", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        audit_tx_summary(audit, tx, "update", "fail", "commit", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_tx_summary(audit, tx, "update", "ok", "ok", "");
    return true;
}

bool launcher_instance_remove_artifact_from_instance(const launcher_services_api_v1* services,
                                                     const std::string& instance_id,
                                                     u32 content_type,
                                                     const std::string& content_id,
                                                     const std::string& state_root_override,
                                                     LauncherInstanceManifest& out_updated_manifest,
                                                     LauncherAuditLog* audit) {
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    size_t idx = 0u;

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);

    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_REMOVE, tx, audit)) {
        return false;
    }
    if (content_id.empty() || content_type == (u32)LAUNCHER_CONTENT_UNKNOWN) {
        audit_tx_summary(audit, tx, "remove", "fail", "bad_key", "");
        return false;
    }
    if (!find_entry_index(tx.before_manifest, content_type, content_id, idx)) {
        audit_tx_summary(audit, tx, "remove", "fail", "missing_entry", "");
        return false;
    }

    after = tx.before_manifest;
    after.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    after.previous_manifest_hash64 = tx.before_manifest_hash64;
    after.known_good = 0u;
    after.last_verified_timestamp_us = 0ull;

    after.content_entries.erase(after.content_entries.begin() + (std::vector<LauncherContentEntry>::difference_type)idx);

    tx.after_manifest = after;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(after);

    audit_tx_summary(audit, tx, "remove", "start", "start", "");
    audit_tx_entry_list(audit, tx.tx_id, "before", tx.before_manifest);
    audit_tx_entry_list(audit, tx.tx_id, "after", tx.after_manifest);

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        audit_tx_summary(audit, tx, "remove", "fail", "stage", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        audit_tx_summary(audit, tx, "remove", "fail", "verify", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        audit_tx_summary(audit, tx, "remove", "fail", "commit", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_tx_summary(audit, tx, "remove", "ok", "ok", "");
    return true;
}

bool launcher_instance_verify_or_repair(const launcher_services_api_v1* services,
                                        const std::string& instance_id,
                                        const std::string& state_root_override,
                                        u32 repair_mode,
                                        LauncherInstanceManifest& out_updated_manifest,
                                        LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    std::string preflight_code;
    LauncherInstancePaths paths;
    std::vector<unsigned char> staged_payload_refs_bytes;

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);

    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      repair_mode ? (u32)LAUNCHER_INSTANCE_TX_OP_REPAIR : (u32)LAUNCHER_INSTANCE_TX_OP_VERIFY,
                                      tx, audit)) {
        return false;
    }

    if (!preflight_verify_for_repair(services, tx.state_root, tx.before_manifest, repair_mode, after, preflight_code)) {
        audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "fail", preflight_code, "");
        return false;
    }

    after.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    after.previous_manifest_hash64 = tx.before_manifest_hash64;
    after.known_good = 1u;
    after.last_verified_timestamp_us = tx.tx_id;

    tx.after_manifest = after;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(after);

    audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "start", "start", "");
    audit_tx_entry_list(audit, tx.tx_id, "before", tx.before_manifest);
    audit_tx_entry_list(audit, tx.tx_id, "after", tx.after_manifest);

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "fail", "stage", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "fail", "verify", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    if (!fs) {
        audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "fail", "missing_fs", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    paths = launcher_instance_paths_make(tx.state_root, tx.instance_id);
    if (!fs_read_all(fs, path_join(paths.staging_root, "payload_refs.tlv"), staged_payload_refs_bytes)) {
        audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "fail", "read_staged_payload_refs", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!write_known_good_staging(services, paths, tx, staged_payload_refs_bytes, audit)) {
        audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "fail", "stage_known_good", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    if (!launcher_instance_tx_commit(services, tx, audit)) {
        audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "fail", "commit", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_tx_summary(audit, tx, repair_mode ? "repair" : "verify", "ok", "ok", "");
    return true;
}

bool launcher_instance_rollback_to_known_good(const launcher_services_api_v1* services,
                                              const std::string& instance_id,
                                              const std::string& state_root_override,
                                              const std::string& cause,
                                              u64 source_tx_id,
                                              LauncherInstanceManifest& out_restored_manifest,
                                              LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstanceTx tx;
    LauncherInstancePaths paths;
    std::vector<unsigned char> kg_bytes;
    LauncherInstanceKnownGoodPointer kg;
    std::vector<unsigned char> snap_manifest_bytes;
    LauncherInstanceManifest snap_manifest;
    std::string snapshot_root;
    std::string snapshot_manifest_path;

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);

    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_ROLLBACK, tx, audit)) {
        return false;
    }

    if (!fs) {
        audit_tx_summary(audit, tx, "rollback", "fail", "missing_fs", "");
        return false;
    }

    paths = launcher_instance_paths_make(tx.state_root, tx.instance_id);
    if (!fs_read_all(fs, path_join(paths.instance_root, "known_good.tlv"), kg_bytes)) {
        audit_tx_summary(audit, tx, "rollback", "fail", "missing_known_good", "");
        return false;
    }
    if (!launcher_instance_known_good_from_tlv_bytes(kg_bytes.empty() ? (const unsigned char*)0 : &kg_bytes[0], kg_bytes.size(), kg)) {
        audit_tx_summary(audit, tx, "rollback", "fail", "decode_known_good", "");
        return false;
    }
    if (kg.previous_dir.empty()) {
        audit_tx_summary(audit, tx, "rollback", "fail", "known_good_empty", "");
        return false;
    }

    snapshot_root = path_join(paths.previous_root, kg.previous_dir);
    snapshot_manifest_path = path_join(snapshot_root, "manifest.tlv");
    if (!fs_read_all(fs, snapshot_manifest_path, snap_manifest_bytes)) {
        audit_tx_summary(audit, tx, "rollback", "fail", "missing_snapshot_manifest", "previous_dir=" + kg.previous_dir);
        return false;
    }
    if (!launcher_instance_manifest_from_tlv_bytes(snap_manifest_bytes.empty() ? (const unsigned char*)0 : &snap_manifest_bytes[0],
                                                   snap_manifest_bytes.size(),
                                                   snap_manifest)) {
        audit_tx_summary(audit, tx, "rollback", "fail", "decode_snapshot_manifest", "previous_dir=" + kg.previous_dir);
        return false;
    }

    snap_manifest.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    snap_manifest.previous_manifest_hash64 = tx.before_manifest_hash64;

    tx.after_manifest = snap_manifest;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(snap_manifest);

    audit_tx_summary(audit, tx, "rollback", "start", "start",
                     std::string("cause=") + cause + ";source_txid=0x" + u64_hex16_string(source_tx_id) + ";previous_dir=" + kg.previous_dir);
    audit_tx_entry_list(audit, tx.tx_id, "before", tx.before_manifest);
    audit_tx_entry_list(audit, tx.tx_id, "after", tx.after_manifest);

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        audit_tx_summary(audit, tx, "rollback", "fail", "stage", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        audit_tx_summary(audit, tx, "rollback", "fail", "verify", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        audit_tx_summary(audit, tx, "rollback", "fail", "commit", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_restored_manifest = tx.after_manifest;
    audit_tx_summary(audit, tx, "rollback", "ok", "ok",
                     std::string("cause=") + cause + ";source_txid=0x" + u64_hex16_string(source_tx_id));
    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
