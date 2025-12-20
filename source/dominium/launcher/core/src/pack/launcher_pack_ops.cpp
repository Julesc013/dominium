/*
FILE: source/dominium/launcher/core/src/pack/launcher_pack_ops.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / pack_ops
RESPONSIBILITY: Implements atomic, instance-scoped pack operations via the transaction engine with deterministic audit.
*/

#include "launcher_pack_ops.h"

#include <cstdio>
#include <cstring>
#include <vector>

#include "launcher_audit.h"
#include "launcher_artifact_store.h"
#include "launcher_instance_ops.h"
#include "launcher_instance_tx.h"
#include "launcher_pack_manifest.h"
#include "launcher_pack_resolver.h"
#include "launcher_safety.h"

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

static bool is_pack_like_type(u32 content_type) {
    return content_type == (u32)LAUNCHER_CONTENT_PACK ||
           content_type == (u32)LAUNCHER_CONTENT_MOD ||
           content_type == (u32)LAUNCHER_CONTENT_RUNTIME;
}

static const char* content_type_name(u32 content_type) {
    switch (content_type) {
    case LAUNCHER_CONTENT_PACK: return "pack";
    case LAUNCHER_CONTENT_MOD: return "mod";
    case LAUNCHER_CONTENT_RUNTIME: return "runtime";
    default: return "unknown";
    }
}

static bool find_entry_index(const LauncherInstanceManifest& m,
                             u32 content_type,
                             const std::string& content_id,
                             size_t& out_index) {
    size_t i;
    for (i = 0u; i < m.content_entries.size(); ++i) {
        if (m.content_entries[i].type == content_type && m.content_entries[i].id == content_id) {
            out_index = i;
            return true;
        }
    }
    return false;
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

static bool fs_file_exists(const launcher_fs_api_v1* fs, const std::string& path) {
    void* fh;
    if (!fs || !fs->file_open || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }
    (void)fs->file_close(fh);
    return true;
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

static bool path_has_dot_segment(const std::string& p) {
    std::string n = normalize_seps(p);
    size_t i = 0u;
    while (i < n.size()) {
        while (i < n.size() && n[i] == '/') {
            ++i;
        }
        if (i >= n.size()) {
            break;
        }
        size_t j = i;
        while (j < n.size() && n[j] != '/') {
            ++j;
        }
        const size_t len = j - i;
        if (len == 1u && n[i] == '.') {
            return true;
        }
        if (len == 2u && n[i] == '.' && n[i + 1u] == '.') {
            return true;
        }
        i = j;
    }
    return false;
}

static bool is_safe_instance_rel_path(const std::string& rel, std::string& out_why) {
    std::string n = normalize_seps(rel);
    size_t i;
    out_why.clear();
    if (n.empty()) {
        out_why = "empty_path";
        return false;
    }
    if (n[0] == '/' || n[0] == '\\') {
        out_why = "absolute_path";
        return false;
    }
    for (i = 0u; i < n.size(); ++i) {
        if ((unsigned char)n[i] == 0u) {
            out_why = "nul_in_path";
            return false;
        }
        if (n[i] == ':') {
            out_why = "drive_path";
            return false;
        }
    }
    if (path_has_dot_segment(n)) {
        out_why = "dot_segment";
        return false;
    }
    return true;
}

static bool load_pack_manifest_for_entry(const launcher_services_api_v1* services,
                                         const std::string& state_root,
                                         const LauncherContentEntry& entry,
                                         LauncherPackManifest& out_manifest,
                                         std::string& out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    std::vector<unsigned char> payload;
    LauncherPackManifest pm;
    std::string verr;
    u32 expected_type = (u32)LAUNCHER_CONTENT_UNKNOWN;

    out_error.clear();
    if (!services || !fs) {
        out_error = "missing_services_or_fs";
        return false;
    }
    if (!is_pack_like_type(entry.type)) {
        out_error = "not_pack_like_entry";
        return false;
    }
    if (entry.id.empty() || entry.version.empty()) {
        out_error = "bad_entry_id_or_version";
        return false;
    }
    if (entry.hash_bytes.empty()) {
        out_error = "missing_entry_hash_bytes";
        return false;
    }

    if (!launcher_artifact_store_paths(state_root, entry.hash_bytes, dir, meta_path, payload_path)) {
        out_error = "artifact_store_paths_failed";
        return false;
    }
    if (!fs_read_all(fs, payload_path, payload)) {
        out_error = std::string("pack_manifest_payload_missing;path=") + payload_path;
        return false;
    }
    if (!launcher_pack_manifest_from_tlv_bytes(payload.empty() ? (const unsigned char*)0 : &payload[0], payload.size(), pm)) {
        out_error = "pack_manifest_decode_failed";
        return false;
    }
    if (!launcher_pack_manifest_validate(pm, &verr)) {
        out_error = std::string("pack_manifest_invalid;") + verr;
        return false;
    }

    if (pm.pack_type == (u32)LAUNCHER_PACK_TYPE_CONTENT) expected_type = (u32)LAUNCHER_CONTENT_PACK;
    else if (pm.pack_type == (u32)LAUNCHER_PACK_TYPE_MOD) expected_type = (u32)LAUNCHER_CONTENT_MOD;
    else if (pm.pack_type == (u32)LAUNCHER_PACK_TYPE_RUNTIME) expected_type = (u32)LAUNCHER_CONTENT_RUNTIME;

    if (pm.pack_id != entry.id) {
        out_error = std::string("pack_id_mismatch;expected=") + entry.id + ";got=" + pm.pack_id;
        return false;
    }
    if (pm.version != entry.version) {
        out_error = std::string("pack_version_mismatch;expected=") + entry.version + ";got=" + pm.version;
        return false;
    }
    if (expected_type != entry.type) {
        out_error = "pack_type_mismatch";
        return false;
    }

    out_manifest = pm;
    return true;
}

static bool execute_pack_tasks(const launcher_services_api_v1* services,
                               const LauncherInstancePaths& paths,
                               const std::string& pack_id,
                               const char* list_name,
                               const std::vector<LauncherPackTask>& tasks,
                               LauncherAuditLog* audit,
                               std::string& out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    size_t i;
    out_error.clear();
    if (!services || !fs) {
        out_error = "missing_services_or_fs";
        return false;
    }
    for (i = 0u; i < tasks.size(); ++i) {
        const LauncherPackTask& t = tasks[i];
        std::string why;
        std::string full;
        if (t.kind != (u32)LAUNCHER_PACK_TASK_REQUIRE_FILE) {
            out_error = std::string("unknown_task_kind;kind=0x") + u64_hex16_string((u64)t.kind);
            return false;
        }
        if (!is_safe_instance_rel_path(t.path, why)) {
            out_error = std::string("task_path_unsafe;why=") + why + ";path=" + t.path;
            return false;
        }
        full = path_join(paths.instance_root, t.path);
        if (!fs_file_exists(fs, full)) {
            out_error = std::string("task_require_file_missing;path=") + t.path;
            return false;
        }
        audit_reason(audit,
                     std::string("pack_task;pack_id=") + pack_id +
                         ";list=" + (list_name ? list_name : "") +
                         ";kind=require_file;path=" + t.path);
    }
    return true;
}

static std::string resolved_or_error_summary(const std::vector<LauncherResolvedPack>& resolved,
                                             const std::string& err) {
    if (!resolved.empty()) {
        return launcher_pack_resolved_order_summary(resolved);
    }
    if (!err.empty()) {
        return std::string("error:") + err;
    }
    return std::string();
}

static void audit_pack_op_begin(LauncherAuditLog* audit,
                                const char* op,
                                const std::string& instance_id,
                                u32 content_type,
                                const std::string& pack_id,
                                const std::string& version) {
    audit_reason(audit,
                 std::string("pack_op;phase=begin;op=") + (op ? op : "") +
                     ";instance_id=" + instance_id +
                     ";content_type=" + content_type_name(content_type) +
                     ";pack_id=" + pack_id +
                     ";version=" + version);
}

static void audit_pack_op_result(LauncherAuditLog* audit,
                                 const char* op,
                                 const LauncherInstanceTx& tx,
                                 const std::string& pack_id,
                                 const std::string& version,
                                 u32 before_enabled,
                                 u32 after_enabled,
                                 const std::string& resolved_order,
                                 const char* result,
                                 const char* code,
                                 const std::string& detail) {
    audit_reason(audit,
                 std::string("pack_op;phase=end;op=") + (op ? op : "") +
                     ";result=" + (result ? result : "") +
                     ";code=" + (code ? code : "") +
                     ";instance_id=" + tx.instance_id +
                     ";txid=0x" + u64_hex16_string(tx.tx_id) +
                     ";pack_id=" + pack_id +
                     ";version=" + version +
                     ";before_enabled=" + (before_enabled ? "1" : "0") +
                     ";after_enabled=" + (after_enabled ? "1" : "0") +
                     ";before_manifest_hash64=0x" + u64_hex16_string(tx.before_manifest_hash64) +
                     ";after_manifest_hash64=0x" + u64_hex16_string(tx.after_manifest_hash64) +
                     ";resolved_order=" + resolved_order +
                     (detail.empty() ? std::string() : (std::string(";detail=") + detail)));
}

static std::vector<LauncherContentEntry> remove_entry_at(const std::vector<LauncherContentEntry>& in,
                                                         size_t remove_index) {
    std::vector<LauncherContentEntry> out;
    size_t i;
    out.reserve(in.size() ? (in.size() - 1u) : 0u);
    for (i = 0u; i < in.size(); ++i) {
        if (i == remove_index) {
            continue;
        }
        out.push_back(in[i]);
    }
    return out;
}

} /* namespace */

bool launcher_pack_install_pack_to_instance(const launcher_services_api_v1* services,
                                            const std::string& instance_id,
                                            const LauncherContentEntry& pack_entry,
                                            const std::string& state_root_override,
                                            LauncherInstanceManifest& out_updated_manifest,
                                            LauncherAuditLog* audit,
                                            std::string* out_error) {
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    LauncherContentEntry e = pack_entry;
    size_t existing_index = 0u;
    std::vector<LauncherResolvedPack> resolved;
    std::string resolve_err;
    std::string tasks_err;
    LauncherPackManifest pm;

    if (out_error) {
        out_error->clear();
    }

    audit_pack_op_begin(audit, "install", instance_id, e.type, e.id, e.version);

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);
    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_INSTALL, tx, audit)) {
        if (out_error) *out_error = "tx_prepare_failed";
        return false;
    }

    if (!is_pack_like_type(e.type) || e.id.empty() || e.version.empty() || e.hash_bytes.empty()) {
        if (out_error) *out_error = "bad_pack_entry";
        audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, 0u, "", "fail", "bad_pack_entry", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (find_entry_index(tx.before_manifest, e.type, e.id, existing_index)) {
        if (out_error) *out_error = "already_installed";
        audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, 0u, "", "fail", "already_installed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    e.enabled = e.enabled ? 1u : 0u;
    if (e.update_policy != (u32)LAUNCHER_UPDATE_NEVER &&
        e.update_policy != (u32)LAUNCHER_UPDATE_PROMPT &&
        e.update_policy != (u32)LAUNCHER_UPDATE_AUTO) {
        e.update_policy = (u32)LAUNCHER_UPDATE_PROMPT;
    }
    e.has_explicit_order_override = e.has_explicit_order_override ? 1u : 0u;

    after = tx.before_manifest;
    after.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    after.previous_manifest_hash64 = tx.before_manifest_hash64;
    after.known_good = 0u;
    after.last_verified_timestamp_us = 0ull;
    after.content_entries.push_back(e);

    tx.after_manifest = after;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(after);

    if (!launcher_pack_resolve_enabled(services, tx.after_manifest, tx.state_root, resolved, &resolve_err)) {
        if (out_error) *out_error = resolve_err;
        audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, e.enabled,
                             resolved_or_error_summary(resolved, resolve_err),
                             "fail", "dependency_resolution_failed", resolve_err);
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    if (!load_pack_manifest_for_entry(services, tx.state_root, e, pm, tasks_err)) {
        if (out_error) *out_error = tasks_err;
        audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, e.enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "pack_manifest_load_failed", tasks_err);
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    {
        LauncherInstancePaths paths = launcher_instance_paths_make(tx.state_root, tx.instance_id);
        if (!execute_pack_tasks(services, paths, e.id, "install", pm.install_tasks, audit, tasks_err)) {
            if (out_error) *out_error = tasks_err;
            audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, e.enabled,
                                 launcher_pack_resolved_order_summary(resolved),
                                 "fail", "install_tasks_failed", tasks_err);
            (void)launcher_instance_tx_rollback(services, tx, audit);
            return false;
        }
    }

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        if (out_error) *out_error = "tx_stage_failed";
        audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, e.enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_stage_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        if (out_error) *out_error = "tx_verify_failed";
        audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, e.enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_verify_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        if (out_error) *out_error = "tx_commit_failed";
        audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, e.enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_commit_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_pack_op_result(audit, "install", tx, e.id, e.version, 0u, e.enabled,
                         launcher_pack_resolved_order_summary(resolved),
                         "ok", "ok", "");
    return true;
}

bool launcher_pack_remove_pack_from_instance(const launcher_services_api_v1* services,
                                             const std::string& instance_id,
                                             u32 content_type,
                                             const std::string& pack_id,
                                             const std::string& state_root_override,
                                             LauncherInstanceManifest& out_updated_manifest,
                                             LauncherAuditLog* audit,
                                             std::string* out_error) {
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    size_t idx = 0u;
    u32 before_enabled = 0u;
    std::vector<LauncherResolvedPack> resolved;
    std::string resolve_err;

    if (out_error) {
        out_error->clear();
    }

    audit_pack_op_begin(audit, "remove", instance_id, content_type, pack_id, "");

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);
    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_REMOVE, tx, audit)) {
        if (out_error) *out_error = "tx_prepare_failed";
        return false;
    }

    if (!is_pack_like_type(content_type) || pack_id.empty()) {
        if (out_error) *out_error = "bad_pack_id";
        audit_pack_op_result(audit, "remove", tx, pack_id, "", 0u, 0u, "", "fail", "bad_pack_id", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!find_entry_index(tx.before_manifest, content_type, pack_id, idx)) {
        if (out_error) *out_error = "missing_entry";
        audit_pack_op_result(audit, "remove", tx, pack_id, "", 0u, 0u, "", "fail", "missing_entry", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    before_enabled = tx.before_manifest.content_entries[idx].enabled ? 1u : 0u;

    after = tx.before_manifest;
    after.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    after.previous_manifest_hash64 = tx.before_manifest_hash64;
    after.known_good = 0u;
    after.last_verified_timestamp_us = 0ull;
    after.content_entries = remove_entry_at(after.content_entries, idx);

    tx.after_manifest = after;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(after);

    if (!launcher_pack_resolve_enabled(services, tx.after_manifest, tx.state_root, resolved, &resolve_err)) {
        if (out_error) *out_error = resolve_err;
        audit_pack_op_result(audit, "remove", tx, pack_id, "", before_enabled, 0u,
                             resolved_or_error_summary(resolved, resolve_err),
                             "fail", "dependency_resolution_failed", resolve_err);
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        if (out_error) *out_error = "tx_stage_failed";
        audit_pack_op_result(audit, "remove", tx, pack_id, "", before_enabled, 0u,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_stage_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        if (out_error) *out_error = "tx_verify_failed";
        audit_pack_op_result(audit, "remove", tx, pack_id, "", before_enabled, 0u,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_verify_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        if (out_error) *out_error = "tx_commit_failed";
        audit_pack_op_result(audit, "remove", tx, pack_id, "", before_enabled, 0u,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_commit_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_pack_op_result(audit, "remove", tx, pack_id, "", before_enabled, 0u,
                         launcher_pack_resolved_order_summary(resolved),
                         "ok", "ok", "");
    return true;
}

bool launcher_pack_update_pack_in_instance(const launcher_services_api_v1* services,
                                           const std::string& instance_id,
                                           const LauncherContentEntry& new_entry,
                                           const std::string& state_root_override,
                                           u32 override_prompt,
                                           LauncherInstanceManifest& out_updated_manifest,
                                           LauncherAuditLog* audit,
                                           std::string* out_error) {
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    size_t idx = 0u;
    u32 policy = 0u;
    u32 before_enabled = 0u;
    std::vector<LauncherResolvedPack> resolved;
    std::string resolve_err;
    std::string tasks_err;
    LauncherPackManifest pm;

    if (out_error) {
        out_error->clear();
    }

    audit_pack_op_begin(audit, "update", instance_id, new_entry.type, new_entry.id, new_entry.version);

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);
    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_UPDATE, tx, audit)) {
        if (out_error) *out_error = "tx_prepare_failed";
        return false;
    }

    if (!is_pack_like_type(new_entry.type) || new_entry.id.empty() || new_entry.version.empty() || new_entry.hash_bytes.empty()) {
        if (out_error) *out_error = "bad_pack_entry";
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             0u, 0u, "", "fail", "bad_pack_entry", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!find_entry_index(tx.before_manifest, new_entry.type, new_entry.id, idx)) {
        if (out_error) *out_error = "missing_entry";
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             0u, 0u, "", "fail", "missing_entry", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    before_enabled = tx.before_manifest.content_entries[idx].enabled ? 1u : 0u;
    policy = tx.before_manifest.content_entries[idx].update_policy;
    if (policy == (u32)LAUNCHER_UPDATE_NEVER) {
        if (out_error) *out_error = "update_policy_never";
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             before_enabled, before_enabled,
                             "", "fail", "update_policy_never", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (policy == (u32)LAUNCHER_UPDATE_PROMPT && !override_prompt) {
        if (out_error) *out_error = "update_policy_prompt_requires_override";
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             before_enabled, before_enabled,
                             "", "fail", "update_policy_prompt_requires_override", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
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

    if (!launcher_pack_resolve_enabled(services, tx.after_manifest, tx.state_root, resolved, &resolve_err)) {
        if (out_error) *out_error = resolve_err;
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             before_enabled, before_enabled,
                             resolved_or_error_summary(resolved, resolve_err),
                             "fail", "dependency_resolution_failed", resolve_err);
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    if (!load_pack_manifest_for_entry(services, tx.state_root, after.content_entries[idx], pm, tasks_err)) {
        if (out_error) *out_error = tasks_err;
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             before_enabled, before_enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "pack_manifest_load_failed", tasks_err);
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    {
        LauncherInstancePaths paths = launcher_instance_paths_make(tx.state_root, tx.instance_id);
        if (!execute_pack_tasks(services, paths, new_entry.id, "verify", pm.verify_tasks, audit, tasks_err)) {
            if (out_error) *out_error = tasks_err;
            audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                                 before_enabled, before_enabled,
                                 launcher_pack_resolved_order_summary(resolved),
                                 "fail", "verify_tasks_failed", tasks_err);
            (void)launcher_instance_tx_rollback(services, tx, audit);
            return false;
        }
    }

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        if (out_error) *out_error = "tx_stage_failed";
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             before_enabled, before_enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_stage_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        if (out_error) *out_error = "tx_verify_failed";
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             before_enabled, before_enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_verify_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        if (out_error) *out_error = "tx_commit_failed";
        audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                             before_enabled, before_enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_commit_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_pack_op_result(audit, "update", tx, new_entry.id, new_entry.version,
                         before_enabled, before_enabled,
                         launcher_pack_resolved_order_summary(resolved),
                         "ok", "ok",
                         std::string("override_prompt=") + (override_prompt ? "1" : "0"));
    return true;
}

bool launcher_pack_set_enabled_in_instance(const launcher_services_api_v1* services,
                                           const std::string& instance_id,
                                           u32 content_type,
                                           const std::string& pack_id,
                                           u32 enabled,
                                           const std::string& state_root_override,
                                           LauncherInstanceManifest& out_updated_manifest,
                                           LauncherAuditLog* audit,
                                           std::string* out_error) {
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    size_t idx = 0u;
    u32 before_enabled = 0u;
    u32 after_enabled = enabled ? 1u : 0u;
    std::vector<LauncherResolvedPack> resolved;
    std::string resolve_err;

    if (out_error) {
        out_error->clear();
    }

    audit_pack_op_begin(audit, "set_enabled", instance_id, content_type, pack_id, "");

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);
    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_UPDATE, tx, audit)) {
        if (out_error) *out_error = "tx_prepare_failed";
        return false;
    }

    if (!is_pack_like_type(content_type) || pack_id.empty()) {
        if (out_error) *out_error = "bad_pack_id";
        audit_pack_op_result(audit, "set_enabled", tx, pack_id, "", 0u, 0u, "", "fail", "bad_pack_id", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!find_entry_index(tx.before_manifest, content_type, pack_id, idx)) {
        if (out_error) *out_error = "missing_entry";
        audit_pack_op_result(audit, "set_enabled", tx, pack_id, "", 0u, 0u, "", "fail", "missing_entry", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    before_enabled = tx.before_manifest.content_entries[idx].enabled ? 1u : 0u;

    if (before_enabled == after_enabled) {
        out_updated_manifest = tx.before_manifest;
        audit_pack_op_result(audit, "set_enabled", tx, pack_id, "",
                             before_enabled, after_enabled,
                             "", "ok", "no_change", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return true;
    }

    after = tx.before_manifest;
    after.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    after.previous_manifest_hash64 = tx.before_manifest_hash64;
    after.known_good = 0u;
    after.last_verified_timestamp_us = 0ull;
    after.content_entries[idx].enabled = after_enabled;

    tx.after_manifest = after;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(after);

    if (!launcher_pack_resolve_enabled(services, tx.after_manifest, tx.state_root, resolved, &resolve_err)) {
        if (out_error) *out_error = resolve_err;
        audit_pack_op_result(audit, "set_enabled", tx, pack_id, "",
                             before_enabled, after_enabled,
                             resolved_or_error_summary(resolved, resolve_err),
                             "fail", "dependency_resolution_failed", resolve_err);
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        if (out_error) *out_error = "tx_stage_failed";
        audit_pack_op_result(audit, "set_enabled", tx, pack_id, "",
                             before_enabled, after_enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_stage_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        if (out_error) *out_error = "tx_verify_failed";
        audit_pack_op_result(audit, "set_enabled", tx, pack_id, "",
                             before_enabled, after_enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_verify_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        if (out_error) *out_error = "tx_commit_failed";
        audit_pack_op_result(audit, "set_enabled", tx, pack_id, "",
                             before_enabled, after_enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_commit_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_pack_op_result(audit, "set_enabled", tx, pack_id, "",
                         before_enabled, after_enabled,
                         launcher_pack_resolved_order_summary(resolved),
                         "ok", "ok", "");
    return true;
}

bool launcher_pack_set_order_override_in_instance(const launcher_services_api_v1* services,
                                                  const std::string& instance_id,
                                                  u32 content_type,
                                                  const std::string& pack_id,
                                                  u32 has_override,
                                                  i32 override_value,
                                                  const std::string& state_root_override,
                                                  LauncherInstanceManifest& out_updated_manifest,
                                                  LauncherAuditLog* audit,
                                                  std::string* out_error) {
    LauncherInstanceTx tx;
    LauncherInstanceManifest after;
    size_t idx = 0u;
    std::vector<LauncherResolvedPack> resolved;
    std::string resolve_err;
    u32 enabled = 0u;
    u32 before_has = 0u;
    i32 before_val = 0;

    if (out_error) {
        out_error->clear();
    }

    audit_pack_op_begin(audit, "set_order_override", instance_id, content_type, pack_id, "");

    (void)launcher_instance_tx_recover_staging(services, instance_id, state_root_override, audit);
    if (!launcher_instance_tx_prepare(services, instance_id, state_root_override,
                                      (u32)LAUNCHER_INSTANCE_TX_OP_UPDATE, tx, audit)) {
        if (out_error) *out_error = "tx_prepare_failed";
        return false;
    }

    if (!is_pack_like_type(content_type) || pack_id.empty()) {
        if (out_error) *out_error = "bad_pack_id";
        audit_pack_op_result(audit, "set_order_override", tx, pack_id, "", 0u, 0u, "", "fail", "bad_pack_id", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!find_entry_index(tx.before_manifest, content_type, pack_id, idx)) {
        if (out_error) *out_error = "missing_entry";
        audit_pack_op_result(audit, "set_order_override", tx, pack_id, "", 0u, 0u, "", "fail", "missing_entry", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    enabled = tx.before_manifest.content_entries[idx].enabled ? 1u : 0u;
    before_has = tx.before_manifest.content_entries[idx].has_explicit_order_override ? 1u : 0u;
    before_val = tx.before_manifest.content_entries[idx].explicit_order_override;

    has_override = has_override ? 1u : 0u;
    if (before_has == has_override && (!has_override || before_val == override_value)) {
        out_updated_manifest = tx.before_manifest;
        audit_pack_op_result(audit, "set_order_override", tx, pack_id, "", enabled, enabled, "", "ok", "no_change", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return true;
    }

    after = tx.before_manifest;
    after.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    after.previous_manifest_hash64 = tx.before_manifest_hash64;
    after.known_good = 0u;
    after.last_verified_timestamp_us = 0ull;
    after.content_entries[idx].has_explicit_order_override = has_override;
    after.content_entries[idx].explicit_order_override = override_value;

    tx.after_manifest = after;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(after);

    if (!launcher_pack_resolve_enabled(services, tx.after_manifest, tx.state_root, resolved, &resolve_err)) {
        if (out_error) *out_error = resolve_err;
        audit_pack_op_result(audit, "set_order_override", tx, pack_id, "", enabled, enabled,
                             resolved_or_error_summary(resolved, resolve_err),
                             "fail", "dependency_resolution_failed", resolve_err);
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    if (!launcher_instance_tx_stage(services, tx, audit)) {
        if (out_error) *out_error = "tx_stage_failed";
        audit_pack_op_result(audit, "set_order_override", tx, pack_id, "", enabled, enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_stage_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_verify(services, tx, audit)) {
        if (out_error) *out_error = "tx_verify_failed";
        audit_pack_op_result(audit, "set_order_override", tx, pack_id, "", enabled, enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_verify_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }
    if (!launcher_instance_tx_commit(services, tx, audit)) {
        if (out_error) *out_error = "tx_commit_failed";
        audit_pack_op_result(audit, "set_order_override", tx, pack_id, "", enabled, enabled,
                             launcher_pack_resolved_order_summary(resolved),
                             "fail", "tx_commit_failed", "");
        (void)launcher_instance_tx_rollback(services, tx, audit);
        return false;
    }

    out_updated_manifest = tx.after_manifest;
    audit_pack_op_result(audit, "set_order_override", tx, pack_id, "", enabled, enabled,
                         launcher_pack_resolved_order_summary(resolved),
                         "ok", "ok",
                         std::string("before_has=") + (before_has ? "1" : "0") +
                             ";after_has=" + (has_override ? "1" : "0"));
    return true;
}

bool launcher_pack_prelaunch_validate_instance(const launcher_services_api_v1* services,
                                               const std::string& instance_id,
                                               const std::string& state_root_override,
                                               LauncherAuditLog* audit,
                                               std::string* out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstanceManifest manifest;
    std::vector<LauncherResolvedPack> ordered;
    std::string err;
    std::string state_root = state_root_override;
    LauncherInstancePaths paths;
    size_t i;

    if (out_error) {
        out_error->clear();
    }
    if (!fs) {
        if (out_error) *out_error = "missing_fs";
        return false;
    }
    if (instance_id.empty()) {
        if (out_error) *out_error = "empty_instance_id";
        audit_reason(audit, "pack_prelaunch;result=fail;code=empty_instance_id");
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        if (out_error) *out_error = "unsafe_instance_id";
        audit_reason(audit, std::string("pack_prelaunch;result=fail;code=unsafe_instance_id;instance_id=") + instance_id);
        return false;
    }
    if (state_root.empty()) {
        char buf[260];
        std::memset(buf, 0, sizeof(buf));
        if (!fs->get_path || !fs->get_path(LAUNCHER_FS_PATH_STATE, buf, sizeof(buf))) {
            if (out_error) *out_error = "missing_state_root";
            return false;
        }
        state_root = std::string(buf);
    }

    if (!launcher_instance_load_manifest(services, instance_id, state_root, manifest)) {
        if (out_error) *out_error = "load_manifest_failed";
        audit_reason(audit, std::string("pack_prelaunch;result=fail;code=load_manifest;instance_id=") + instance_id);
        return false;
    }

    if (!launcher_pack_validate_simulation_safety(services, manifest, state_root, &err)) {
        if (out_error) *out_error = err;
        audit_reason(audit, std::string("pack_prelaunch;result=fail;code=sim_safety;instance_id=") + instance_id + ";" + err);
        return false;
    }
    if (!launcher_pack_resolve_enabled(services, manifest, state_root, ordered, &err)) {
        if (out_error) *out_error = err;
        audit_reason(audit, std::string("pack_prelaunch;result=fail;code=resolve;instance_id=") + instance_id + ";" + err);
        return false;
    }

    audit_reason(audit, std::string("pack_prelaunch;result=ok;instance_id=") + instance_id +
                           ";resolved_order=" + launcher_pack_resolved_order_summary(ordered));

    paths = launcher_instance_paths_make(state_root, instance_id);
    for (i = 0u; i < ordered.size(); ++i) {
        const LauncherResolvedPack& rp = ordered[i];
        size_t ent_idx = 0u;
        LauncherPackManifest pm;
        std::string pm_err;
        if (!find_entry_index(manifest, rp.content_type, rp.pack_id, ent_idx)) {
            if (out_error) *out_error = std::string("missing_entry_for_resolved_pack;pack_id=") + rp.pack_id;
            return false;
        }
        if (!load_pack_manifest_for_entry(services, state_root, manifest.content_entries[ent_idx], pm, pm_err)) {
            if (out_error) *out_error = pm_err;
            return false;
        }
        if (!execute_pack_tasks(services, paths, rp.pack_id, "prelaunch", pm.prelaunch_tasks, audit, pm_err)) {
            if (out_error) *out_error = pm_err;
            audit_reason(audit, std::string("pack_prelaunch;result=fail;code=prelaunch_tasks;pack_id=") + rp.pack_id + ";" + pm_err);
            return false;
        }
    }

    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
