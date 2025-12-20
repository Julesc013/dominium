/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance_tx.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_tx
RESPONSIBILITY: Implements transactional instance mutation engine with staging-only writes and deterministic audit.
*/

#include "launcher_instance_tx.h"

#include <cstdio>
#include <cstring>
#include <vector>

#include "launcher_artifact_store.h"
#include "launcher_audit.h"
#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"
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

static const launcher_time_api_v1* get_time(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_TIME_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_time_api_v1*)iface;
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
extern "C" int _rmdir(const char* path);
#else
extern "C" int mkdir(const char* path, unsigned int mode);
extern "C" int rmdir(const char* path);
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

static bool get_state_root(const launcher_fs_api_v1* fs, std::string& out_state_root) {
    char buf[260];
    if (!fs || !fs->get_path) {
        return false;
    }
    std::memset(buf, 0, sizeof(buf));
    if (!fs->get_path(LAUNCHER_FS_PATH_STATE, buf, sizeof(buf))) {
        return false;
    }
    out_state_root = std::string(buf);
    return !out_state_root.empty();
}

static std::string payload_refs_path_live(const LauncherInstancePaths& p) {
    return path_join(p.instance_root, "payload_refs.tlv");
}

static std::string payload_refs_path_staging(const LauncherInstancePaths& p) {
    return path_join(p.staging_root, "payload_refs.tlv");
}

static std::string tx_path_staging(const LauncherInstancePaths& p) {
    return path_join(p.staging_root, "transaction.tlv");
}

static std::string known_good_path_live(const LauncherInstancePaths& p) {
    return path_join(p.instance_root, "known_good.tlv");
}

static std::string known_good_path_staging(const LauncherInstancePaths& p) {
    return path_join(p.staging_root, "known_good.tlv");
}

static std::string known_good_snapshot_root_staging(const LauncherInstancePaths& p) {
    return path_join(p.staging_root, "known_good_snapshot");
}

static std::string known_good_snapshot_manifest_staging(const LauncherInstancePaths& p) {
    return path_join(known_good_snapshot_root_staging(p), "manifest.tlv");
}

static std::string known_good_snapshot_payload_refs_staging(const LauncherInstancePaths& p) {
    return path_join(known_good_snapshot_root_staging(p), "payload_refs.tlv");
}

static bool tx_state_to_tlv_bytes(const LauncherInstanceTx& tx, std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_INSTANCE_TX_TLV_VERSION);
    w.add_u64(LAUNCHER_INSTANCE_TX_TLV_TAG_TX_ID, tx.tx_id);
    w.add_string(LAUNCHER_INSTANCE_TX_TLV_TAG_INSTANCE_ID, tx.instance_id);
    w.add_u32(LAUNCHER_INSTANCE_TX_TLV_TAG_OP_TYPE, tx.op_type);
    w.add_u32(LAUNCHER_INSTANCE_TX_TLV_TAG_PHASE, tx.phase);
    w.add_u64(LAUNCHER_INSTANCE_TX_TLV_TAG_BEFORE_MANIFEST_HASH64, tx.before_manifest_hash64);
    w.add_u64(LAUNCHER_INSTANCE_TX_TLV_TAG_AFTER_MANIFEST_HASH64, tx.after_manifest_hash64);
    out_bytes = w.bytes();
    return true;
}

static bool tx_state_from_tlv_bytes(const unsigned char* data, size_t size, LauncherInstanceTx& out_tx) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;
    LauncherInstanceTx tx;

    if (!data || size == 0u) {
        return false;
    }
    if (!tlv_read_schema_version_or_default(data,
                                            size,
                                            version,
                                            launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_INSTANCE_TX))) {
        return false;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_INSTANCE_TX, version)) {
        return false;
    }
    tx.schema_version = launcher_tlv_schema_current_version(LAUNCHER_TLV_SCHEMA_INSTANCE_TX);
    while (r.next(rec)) {
        if (rec.tag == LAUNCHER_TLV_TAG_SCHEMA_VERSION) {
            continue;
        }
        switch (rec.tag) {
        case LAUNCHER_INSTANCE_TX_TLV_TAG_TX_ID: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                tx.tx_id = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_TX_TLV_TAG_INSTANCE_ID:
            tx.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_INSTANCE_TX_TLV_TAG_OP_TYPE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                tx.op_type = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_TX_TLV_TAG_PHASE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                tx.phase = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_TX_TLV_TAG_BEFORE_MANIFEST_HASH64: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                tx.before_manifest_hash64 = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_TX_TLV_TAG_AFTER_MANIFEST_HASH64: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                tx.after_manifest_hash64 = v;
            }
            break;
        }
        default:
            break; /* skip unknown */
        }
    }
    out_tx = tx;
    return true;
}

static bool write_tx_state(const launcher_fs_api_v1* fs, const LauncherInstancePaths& paths, const LauncherInstanceTx& tx) {
    std::vector<unsigned char> bytes;
    if (!tx_state_to_tlv_bytes(tx, bytes)) {
        return false;
    }
    return fs_write_all(fs, tx_path_staging(paths), bytes);
}

static bool read_tx_state(const launcher_fs_api_v1* fs, const LauncherInstancePaths& paths, LauncherInstanceTx& out_tx) {
    std::vector<unsigned char> bytes;
    if (!fs_read_all(fs, tx_path_staging(paths), bytes)) {
        return false;
    }
    return tx_state_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), out_tx);
}

static bool build_payload_refs_and_verify(const launcher_services_api_v1* services,
                                          const LauncherInstanceTx& tx,
                                          LauncherInstancePayloadRefs& out_refs) {
    LauncherInstancePayloadRefs refs;
    size_t i;

    refs.schema_version = LAUNCHER_INSTANCE_PAYLOAD_REFS_TLV_VERSION;
    refs.instance_id = tx.after_manifest.instance_id;
    refs.manifest_hash64 = tx.after_manifest_hash64;
    refs.entries.clear();

    for (i = 0u; i < tx.after_manifest.content_entries.size(); ++i) {
        const LauncherContentEntry& e = tx.after_manifest.content_entries[i];
        LauncherArtifactMetadata meta;
        LauncherPayloadRefEntry re;

        if (e.enabled == 0u) {
            continue;
        }
        if (e.hash_bytes.empty()) {
            return false;
        }
        if (!launcher_artifact_store_verify(services, tx.state_root, e.hash_bytes, e.type, meta)) {
            return false;
        }
        re.type = e.type;
        re.id = e.id;
        re.version = e.version;
        re.hash_bytes = e.hash_bytes;
        re.size_bytes = meta.size_bytes;
        re.store_algo = std::string(launcher_artifact_store_default_algo());
        refs.entries.push_back(re);
    }

    out_refs = refs;
    return true;
}

} /* namespace */

LauncherInstanceTx::LauncherInstanceTx()
    : schema_version(LAUNCHER_INSTANCE_TX_TLV_VERSION),
      tx_id(0ull),
      instance_id(),
      state_root(),
      op_type(0u),
      phase((u32)LAUNCHER_INSTANCE_TX_PHASE_NONE),
      before_manifest_hash64(0ull),
      after_manifest_hash64(0ull),
      before_manifest(),
      after_manifest() {
}

bool launcher_instance_tx_recover_staging(const launcher_services_api_v1* services,
                                          const std::string& instance_id,
                                          const std::string& state_root_override,
                                          LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    LauncherInstancePaths paths;
    std::string tx_path;
    LauncherInstanceTx tx;

    if (!services || !fs) {
        return false;
    }
    if (instance_id.empty()) {
        audit_reason(audit, "instance_tx_recover;result=fail;code=empty_instance_id");
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        audit_reason(audit, std::string("instance_tx_recover;result=fail;code=unsafe_instance_id;instance_id=") + instance_id);
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        return false;
    }

    paths = launcher_instance_paths_make(state_root, instance_id);
    tx_path = tx_path_staging(paths);
    if (!fs_file_exists(fs, tx_path)) {
        return true; /* nothing to recover */
    }

    /* Best-effort: read tx state for audit, then delete staging artifacts. */
    if (read_tx_state(fs, paths, tx)) {
        audit_reason(audit,
                     std::string("instance_tx_recover;instance_id=") + instance_id +
                         ";txid=0x" + u64_hex16_string(tx.tx_id) +
                         ";op=" + u64_hex16_string((u64)tx.op_type) +
                         ";phase=" + u64_hex16_string((u64)tx.phase));
    } else {
        audit_reason(audit, std::string("instance_tx_recover;instance_id=") + instance_id + ";tx_read_failed=1");
    }

    remove_file_best_effort(paths.staging_manifest_path);
    remove_file_best_effort(payload_refs_path_staging(paths));
    remove_file_best_effort(known_good_path_staging(paths));
    remove_file_best_effort(known_good_snapshot_manifest_staging(paths));
    remove_file_best_effort(known_good_snapshot_payload_refs_staging(paths));
    rmdir_best_effort(known_good_snapshot_root_staging(paths));
    remove_file_best_effort(tx_path);
    /* Leave staging directory itself in place (layout contract). */
    return true;
}

bool launcher_instance_tx_prepare(const launcher_services_api_v1* services,
                                  const std::string& instance_id,
                                  const std::string& state_root_override,
                                  u32 op_type,
                                  LauncherInstanceTx& out_tx,
                                  LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time = get_time(services);
    std::string state_root;
    LauncherInstanceManifest live;
    LauncherInstanceTx tx;
    LauncherInstancePaths paths;

    if (!services || !fs || !time || !time->now_us) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=missing_services;instance_id=") + instance_id);
        return false;
    }
    if (instance_id.empty()) {
        audit_reason(audit, "instance_tx;result=fail;code=empty_instance_id");
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=unsafe_instance_id;instance_id=") + instance_id);
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=state_root_unavailable;instance_id=") + instance_id);
        return false;
    }

    if (!launcher_instance_load_manifest(services, instance_id, state_root, live)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=read_manifest;instance_id=") + instance_id);
        return false;
    }

    tx.schema_version = LAUNCHER_INSTANCE_TX_TLV_VERSION;
    tx.tx_id = time->now_us();
    tx.instance_id = instance_id;
    tx.state_root = state_root;
    tx.op_type = op_type;
    tx.phase = (u32)LAUNCHER_INSTANCE_TX_PHASE_PREPARE;
    tx.before_manifest = live;
    tx.after_manifest = live;
    tx.before_manifest_hash64 = launcher_instance_manifest_hash64(live);
    tx.after_manifest_hash64 = tx.before_manifest_hash64;

    paths = launcher_instance_paths_make(state_root, instance_id);
    (void)mkdir_p_best_effort(paths.staging_root);

    if (!write_tx_state(fs, paths, tx)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=write_tx_state;instance_id=") + instance_id);
        return false;
    }

    out_tx = tx;
    audit_reason(audit,
                 std::string("instance_tx;result=ok;phase=prepare;instance_id=") + instance_id +
                     ";txid=0x" + u64_hex16_string(tx.tx_id) +
                     ";before_manifest_hash64=0x" + u64_hex16_string(tx.before_manifest_hash64));
    return true;
}

bool launcher_instance_tx_stage(const launcher_services_api_v1* services,
                                LauncherInstanceTx& tx,
                                LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstancePaths paths;
    std::vector<unsigned char> bytes;

    if (!services || !fs) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=missing_services;phase=stage;instance_id=") + tx.instance_id);
        return false;
    }
    if (tx.phase != (u32)LAUNCHER_INSTANCE_TX_PHASE_PREPARE) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=bad_phase;phase=stage;instance_id=") + tx.instance_id);
        return false;
    }
    if (tx.instance_id.empty() || tx.state_root.empty()) {
        audit_reason(audit, "instance_tx;result=fail;code=missing_ids;phase=stage");
        return false;
    }
    if (!launcher_is_safe_id_component(tx.instance_id)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=unsafe_instance_id;phase=stage;instance_id=") + tx.instance_id);
        return false;
    }

    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(tx.after_manifest);
    paths = launcher_instance_paths_make(tx.state_root, tx.instance_id);
    (void)mkdir_p_best_effort(paths.staging_root);

    /* Clear any prior staged files (only within staging). */
    remove_file_best_effort(paths.staging_manifest_path);
    remove_file_best_effort(payload_refs_path_staging(paths));
    remove_file_best_effort(known_good_path_staging(paths));
    remove_file_best_effort(known_good_snapshot_manifest_staging(paths));
    remove_file_best_effort(known_good_snapshot_payload_refs_staging(paths));
    rmdir_best_effort(known_good_snapshot_root_staging(paths));

    if (!launcher_instance_manifest_to_tlv_bytes(tx.after_manifest, bytes)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=encode_manifest;phase=stage;instance_id=") + tx.instance_id);
        return false;
    }
    if (!fs_write_all(fs, paths.staging_manifest_path, bytes)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=write_staging_manifest;phase=stage;instance_id=") + tx.instance_id);
        return false;
    }

    tx.phase = (u32)LAUNCHER_INSTANCE_TX_PHASE_STAGE;
    if (!write_tx_state(fs, paths, tx)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=write_tx_state;phase=stage;instance_id=") + tx.instance_id);
        return false;
    }

    audit_reason(audit,
                 std::string("instance_tx;result=ok;phase=stage;instance_id=") + tx.instance_id +
                     ";txid=0x" + u64_hex16_string(tx.tx_id) +
                     ";after_manifest_hash64=0x" + u64_hex16_string(tx.after_manifest_hash64));
    return true;
}

bool launcher_instance_tx_verify(const launcher_services_api_v1* services,
                                 LauncherInstanceTx& tx,
                                 LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstancePaths paths;
    LauncherInstancePayloadRefs refs;
    std::vector<unsigned char> bytes;

    if (!services || !fs) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=missing_services;phase=verify;instance_id=") + tx.instance_id);
        return false;
    }
    if (tx.phase != (u32)LAUNCHER_INSTANCE_TX_PHASE_STAGE) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=bad_phase;phase=verify;instance_id=") + tx.instance_id);
        return false;
    }
    if (tx.instance_id.empty() || tx.state_root.empty()) {
        audit_reason(audit, "instance_tx;result=fail;code=missing_ids;phase=verify");
        return false;
    }
    if (!launcher_is_safe_id_component(tx.instance_id)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=unsafe_instance_id;phase=verify;instance_id=") + tx.instance_id);
        return false;
    }

    paths = launcher_instance_paths_make(tx.state_root, tx.instance_id);

    if (!build_payload_refs_and_verify(services, tx, refs)) {
        audit_reason(audit,
                     std::string("instance_tx;result=fail;code=verify_failed;phase=verify;instance_id=") + tx.instance_id +
                         ";txid=0x" + u64_hex16_string(tx.tx_id));
        return false;
    }
    if (!launcher_instance_payload_refs_to_tlv_bytes(refs, bytes)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=encode_payload_refs;phase=verify;instance_id=") + tx.instance_id);
        return false;
    }
    if (!fs_write_all(fs, payload_refs_path_staging(paths), bytes)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=write_staging_payload_refs;phase=verify;instance_id=") + tx.instance_id);
        return false;
    }

    tx.phase = (u32)LAUNCHER_INSTANCE_TX_PHASE_VERIFY;
    if (!write_tx_state(fs, paths, tx)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=write_tx_state;phase=verify;instance_id=") + tx.instance_id);
        return false;
    }

    audit_reason(audit,
                 std::string("instance_tx;result=ok;phase=verify;instance_id=") + tx.instance_id +
                     ";txid=0x" + u64_hex16_string(tx.tx_id));
    return true;
}

bool launcher_instance_tx_commit(const launcher_services_api_v1* services,
                                 LauncherInstanceTx& tx,
                                 LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstancePaths paths;
    std::string live_payload_refs;
    std::string prev_dir;
    std::string prev_manifest_path;
    std::string prev_payload_refs_path;
    std::string staged_payload_refs;
    bool had_prev_payload_refs = false;
    bool have_staged_known_good_ptr = false;
    bool have_staged_known_good_snapshot = false;
    bool had_live_known_good_ptr = false;
    std::string live_known_good_ptr;
    std::string staged_known_good_ptr;
    std::string archived_known_good_ptr;
    std::string staged_known_good_snapshot_root;
    std::string moved_known_good_snapshot_root;

    if (!services || !fs) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=missing_services;phase=commit;instance_id=") + tx.instance_id);
        return false;
    }
    if (tx.phase != (u32)LAUNCHER_INSTANCE_TX_PHASE_VERIFY) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=bad_phase;phase=commit;instance_id=") + tx.instance_id);
        return false;
    }
    if (tx.instance_id.empty() || tx.state_root.empty()) {
        audit_reason(audit, "instance_tx;result=fail;code=missing_ids;phase=commit");
        return false;
    }
    if (!launcher_is_safe_id_component(tx.instance_id)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=unsafe_instance_id;phase=commit;instance_id=") + tx.instance_id);
        return false;
    }

    paths = launcher_instance_paths_make(tx.state_root, tx.instance_id);
    live_payload_refs = payload_refs_path_live(paths);
    staged_payload_refs = payload_refs_path_staging(paths);
    live_known_good_ptr = known_good_path_live(paths);
    staged_known_good_ptr = known_good_path_staging(paths);
    staged_known_good_snapshot_root = known_good_snapshot_root_staging(paths);

    if (!fs_file_exists(fs, paths.staging_manifest_path) || !fs_file_exists(fs, staged_payload_refs)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=missing_staged_files;phase=commit;instance_id=") + tx.instance_id);
        return false;
    }

    prev_dir = path_join(paths.previous_root, u64_hex16_string(tx.before_manifest_hash64) + "_" + u64_hex16_string(tx.tx_id));
    (void)mkdir_p_best_effort(prev_dir);
    prev_manifest_path = path_join(prev_dir, "manifest.tlv");
    prev_payload_refs_path = path_join(prev_dir, "payload_refs.tlv");

    if (std::rename(paths.manifest_path.c_str(), prev_manifest_path.c_str()) != 0) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=archive_manifest;phase=commit;instance_id=") + tx.instance_id);
        return false;
    }

    if (fs_file_exists(fs, live_payload_refs)) {
        had_prev_payload_refs = true;
        if (std::rename(live_payload_refs.c_str(), prev_payload_refs_path.c_str()) != 0) {
            (void)std::rename(prev_manifest_path.c_str(), paths.manifest_path.c_str());
            audit_reason(audit, std::string("instance_tx;result=fail;code=archive_payload_refs;phase=commit;instance_id=") + tx.instance_id);
            return false;
        }
    }

    if (std::rename(paths.staging_manifest_path.c_str(), paths.manifest_path.c_str()) != 0) {
        /* rollback: restore previous */
        if (had_prev_payload_refs) {
            (void)std::rename(prev_payload_refs_path.c_str(), live_payload_refs.c_str());
        }
        (void)std::rename(prev_manifest_path.c_str(), paths.manifest_path.c_str());
        audit_reason(audit, std::string("instance_tx;result=fail;code=commit_manifest;phase=commit;instance_id=") + tx.instance_id);
        return false;
    }

    if (std::rename(staged_payload_refs.c_str(), live_payload_refs.c_str()) != 0) {
        /* rollback: attempt to restore previous live manifest+refs */
        (void)std::rename(paths.manifest_path.c_str(), paths.staging_manifest_path.c_str());
        if (had_prev_payload_refs) {
            (void)std::rename(prev_payload_refs_path.c_str(), live_payload_refs.c_str());
        }
        (void)std::rename(prev_manifest_path.c_str(), paths.manifest_path.c_str());
        audit_reason(audit, std::string("instance_tx;result=fail;code=commit_payload_refs;phase=commit;instance_id=") + tx.instance_id);
        return false;
    }

    have_staged_known_good_ptr = fs_file_exists(fs, staged_known_good_ptr);
    have_staged_known_good_snapshot = fs_file_exists(fs, known_good_snapshot_manifest_staging(paths)) &&
                                      fs_file_exists(fs, known_good_snapshot_payload_refs_staging(paths));

    if (have_staged_known_good_snapshot) {
        moved_known_good_snapshot_root =
            path_join(paths.previous_root,
                      std::string("known_good_") + u64_hex16_string(tx.after_manifest_hash64) + "_" + u64_hex16_string(tx.tx_id));
        if (std::rename(staged_known_good_snapshot_root.c_str(), moved_known_good_snapshot_root.c_str()) != 0) {
            /* rollback: restore previous live manifest+refs (snapshot remains staged) */
            (void)std::rename(paths.manifest_path.c_str(), paths.staging_manifest_path.c_str());
            (void)std::rename(live_payload_refs.c_str(), staged_payload_refs.c_str());
            if (had_prev_payload_refs) {
                (void)std::rename(prev_payload_refs_path.c_str(), live_payload_refs.c_str());
            }
            (void)std::rename(prev_manifest_path.c_str(), paths.manifest_path.c_str());
            audit_reason(audit, std::string("instance_tx;result=fail;code=commit_known_good_snapshot;phase=commit;instance_id=") + tx.instance_id);
            return false;
        }
    }

    if (have_staged_known_good_ptr) {
        if (fs_file_exists(fs, live_known_good_ptr)) {
            had_live_known_good_ptr = true;
            archived_known_good_ptr = path_join(prev_dir, "known_good.tlv");
            if (std::rename(live_known_good_ptr.c_str(), archived_known_good_ptr.c_str()) != 0) {
                /* rollback: restore previous live manifest+refs and snapshot (best-effort) */
                if (have_staged_known_good_snapshot) {
                    (void)std::rename(moved_known_good_snapshot_root.c_str(), staged_known_good_snapshot_root.c_str());
                }
                (void)std::rename(paths.manifest_path.c_str(), paths.staging_manifest_path.c_str());
                (void)std::rename(live_payload_refs.c_str(), staged_payload_refs.c_str());
                if (had_prev_payload_refs) {
                    (void)std::rename(prev_payload_refs_path.c_str(), live_payload_refs.c_str());
                }
                (void)std::rename(prev_manifest_path.c_str(), paths.manifest_path.c_str());
                audit_reason(audit, std::string("instance_tx;result=fail;code=archive_known_good_ptr;phase=commit;instance_id=") + tx.instance_id);
                return false;
            }
        }
        if (std::rename(staged_known_good_ptr.c_str(), live_known_good_ptr.c_str()) != 0) {
            /* rollback: restore archived known_good pointer if any, and restore previous live manifest+refs */
            if (had_live_known_good_ptr) {
                (void)std::rename(archived_known_good_ptr.c_str(), live_known_good_ptr.c_str());
            }
            if (have_staged_known_good_snapshot) {
                (void)std::rename(moved_known_good_snapshot_root.c_str(), staged_known_good_snapshot_root.c_str());
            }
            (void)std::rename(paths.manifest_path.c_str(), paths.staging_manifest_path.c_str());
            (void)std::rename(live_payload_refs.c_str(), staged_payload_refs.c_str());
            if (had_prev_payload_refs) {
                (void)std::rename(prev_payload_refs_path.c_str(), live_payload_refs.c_str());
            }
            (void)std::rename(prev_manifest_path.c_str(), paths.manifest_path.c_str());
            audit_reason(audit, std::string("instance_tx;result=fail;code=commit_known_good_ptr;phase=commit;instance_id=") + tx.instance_id);
            return false;
        }
    }

    /* Success: transaction artifacts are now live; remove staging tx marker. */
    remove_file_best_effort(tx_path_staging(paths));
    tx.phase = (u32)LAUNCHER_INSTANCE_TX_PHASE_DONE;
    (void)write_tx_state(fs, paths, tx); /* best-effort; may recreate marker but is still within staging */
    remove_file_best_effort(tx_path_staging(paths));

    audit_reason(audit,
                 std::string("instance_tx;result=ok;phase=commit;instance_id=") + tx.instance_id +
                     ";txid=0x" + u64_hex16_string(tx.tx_id) +
                     ";before_manifest_hash64=0x" + u64_hex16_string(tx.before_manifest_hash64) +
                     ";after_manifest_hash64=0x" + u64_hex16_string(tx.after_manifest_hash64));
    return true;
}

bool launcher_instance_tx_rollback(const launcher_services_api_v1* services,
                                   LauncherInstanceTx& tx,
                                   LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstancePaths paths;

    if (!services || !fs) {
        audit_reason(audit, "instance_tx;result=fail;code=missing_services;phase=rollback");
        return false;
    }
    if (tx.instance_id.empty() || tx.state_root.empty()) {
        audit_reason(audit, "instance_tx;result=fail;code=missing_ids;phase=rollback");
        return false;
    }
    if (!launcher_is_safe_id_component(tx.instance_id)) {
        audit_reason(audit, std::string("instance_tx;result=fail;code=unsafe_instance_id;phase=rollback;instance_id=") + tx.instance_id);
        return false;
    }

    paths = launcher_instance_paths_make(tx.state_root, tx.instance_id);

    remove_file_best_effort(paths.staging_manifest_path);
    remove_file_best_effort(payload_refs_path_staging(paths));
    remove_file_best_effort(known_good_path_staging(paths));
    remove_file_best_effort(known_good_snapshot_manifest_staging(paths));
    remove_file_best_effort(known_good_snapshot_payload_refs_staging(paths));
    rmdir_best_effort(known_good_snapshot_root_staging(paths));
    remove_file_best_effort(tx_path_staging(paths));
    /* staging dir kept */

    tx.phase = (u32)LAUNCHER_INSTANCE_TX_PHASE_DONE;
    audit_reason(audit,
                 std::string("instance_tx;result=ok;phase=rollback;instance_id=") + tx.instance_id +
                     ";txid=0x" + u64_hex16_string(tx.tx_id));
    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
