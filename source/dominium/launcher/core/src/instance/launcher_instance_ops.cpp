/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance_ops.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_ops
RESPONSIBILITY: Implements instance root operations with isolated roots, staging/previous swaps, and deterministic audit emission.
*/

#include "launcher_instance_ops.h"

#include <cstdio>
#include <cstring>
#include <vector>

#include "launcher_audit.h"
#include "launcher_safety.h"
#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

enum { LAUNCHER_INSTANCE_CONFIG_TLV_VERSION = 1u };

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
    if (got != (size_t)sz) {
        out_bytes.clear();
        return false;
    }
    return true;
}

static bool fs_copy_file(const launcher_fs_api_v1* fs,
                         const std::string& src_path,
                         const std::string& dst_path) {
    std::vector<unsigned char> bytes;
    if (!fs_read_all(fs, src_path, bytes)) {
        return false;
    }
    return fs_write_all(fs, dst_path, bytes);
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

static bool write_empty_config_file(const launcher_fs_api_v1* fs, const std::string& path) {
    TlvWriter w;
    std::vector<unsigned char> bytes;
    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, (u32)LAUNCHER_INSTANCE_CONFIG_TLV_VERSION);
    bytes = w.bytes();
    return fs_write_all(fs, path, bytes);
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

static bool hash_bytes_match_fnv64_le(const std::vector<unsigned char>& expected_hash_bytes, u64 fnv64) {
    unsigned char le[8];
    size_t i;
    if (expected_hash_bytes.size() != 8u) {
        return false;
    }
    tlv_write_u64_le(le, fnv64);
    for (i = 0u; i < 8u; ++i) {
        if (expected_hash_bytes[i] != le[i]) {
            return false;
        }
    }
    return true;
}

static bool commit_manifest_with_previous(const LauncherInstancePaths& paths,
                                          u64 before_hash64,
                                          u64 stamp_us) {
    std::string prev_dir;
    std::string prev_manifest_path;
    char hhex[17];
    char thex[17];

    u64_to_hex16(before_hash64, hhex);
    u64_to_hex16(stamp_us, thex);

    prev_dir = path_join(paths.previous_root, std::string(hhex) + "_" + std::string(thex));
    (void)mkdir_p_best_effort(prev_dir);
    prev_manifest_path = path_join(prev_dir, "manifest.tlv");

    if (std::rename(paths.manifest_path.c_str(), prev_manifest_path.c_str()) != 0) {
        return false;
    }
    if (std::rename(paths.staging_manifest_path.c_str(), paths.manifest_path.c_str()) != 0) {
        /* Attempt rollback: restore previous manifest to live path. */
        (void)std::rename(prev_manifest_path.c_str(), paths.manifest_path.c_str());
        return false;
    }
    return true;
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

static void audit_instance_op(LauncherAuditLog* audit,
                              const std::string& op,
                              const std::string& instance_id,
                              const std::string& result,
                              const std::string& code,
                              u64 before_hash64,
                              u64 after_hash64,
                              const std::string& extra_kv) {
    std::string line;
    line.reserve(256u);
    line += "instance_op;";
    line += "op=";
    line += op;
    line += ";instance_id=";
    line += instance_id.empty() ? std::string("<empty>") : instance_id;
    line += ";result=";
    line += result;
    line += ";code=";
    line += code;
    line += ";before_hash64=0x";
    line += u64_hex16_string(before_hash64);
    line += ";after_hash64=0x";
    line += u64_hex16_string(after_hash64);
    if (!extra_kv.empty()) {
        line += ";";
        line += extra_kv;
    }
    audit_reason(audit, line);
}

} /* namespace */

LauncherInstancePaths::LauncherInstancePaths()
    : state_root(),
      instances_root(),
      instance_root(),
      manifest_path(),
      config_root(),
      config_file_path(),
      saves_root(),
      mods_root(),
      content_root(),
      cache_root(),
      logs_root(),
      staging_root(),
      staging_manifest_path(),
      previous_root() {
}

LauncherInstancePaths launcher_instance_paths_make(const std::string& state_root,
                                                   const std::string& instance_id) {
    LauncherInstancePaths p;
    p.state_root = normalize_seps(state_root);
    p.instances_root = path_join(p.state_root, "instances");
    p.instance_root = path_join(p.instances_root, instance_id);
    p.manifest_path = path_join(p.instance_root, "manifest.tlv");
    p.config_root = path_join(p.instance_root, "config");
    p.config_file_path = path_join(p.config_root, "config.tlv");
    p.saves_root = path_join(p.instance_root, "saves");
    p.mods_root = path_join(p.instance_root, "mods");
    p.content_root = path_join(p.instance_root, "content");
    p.cache_root = path_join(p.instance_root, "cache");
    p.logs_root = path_join(p.instance_root, "logs");
    p.staging_root = path_join(p.instance_root, "staging");
    p.staging_manifest_path = path_join(p.staging_root, "manifest.tlv");
    p.previous_root = path_join(p.instance_root, "previous");
    return p;
}

bool launcher_instance_ensure_root_layout(const launcher_services_api_v1* services,
                                          const LauncherInstancePaths& paths) {
    const launcher_fs_api_v1* fs = get_fs(services);
    if (!services || !fs) {
        return false;
    }

    (void)mkdir_p_best_effort(paths.instances_root);
    (void)mkdir_p_best_effort(paths.instance_root);
    (void)mkdir_p_best_effort(paths.config_root);
    (void)mkdir_p_best_effort(paths.saves_root);
    (void)mkdir_p_best_effort(paths.mods_root);
    (void)mkdir_p_best_effort(paths.content_root);
    (void)mkdir_p_best_effort(paths.cache_root);
    (void)mkdir_p_best_effort(paths.logs_root);
    (void)mkdir_p_best_effort(paths.staging_root);
    (void)mkdir_p_best_effort(paths.previous_root);

    /* Ensure config file exists as TLV (empty baseline). */
    if (!fs_file_exists(fs, paths.config_file_path)) {
        if (!write_empty_config_file(fs, paths.config_file_path)) {
            return false;
        }
    }
    return true;
}

bool launcher_instance_load_manifest(const launcher_services_api_v1* services,
                                     const std::string& instance_id,
                                     const std::string& state_root_override,
                                     LauncherInstanceManifest& out_manifest) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    LauncherInstancePaths paths;
    std::vector<unsigned char> bytes;

    if (!services || !fs || instance_id.empty()) {
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        return false;
    }

    paths = launcher_instance_paths_make(state_root, instance_id);
    if (!fs_read_all(fs, paths.manifest_path, bytes)) {
        return false;
    }
    if (bytes.empty()) {
        return false;
    }
    return launcher_instance_manifest_from_tlv_bytes(&bytes[0], bytes.size(), out_manifest);
}

bool launcher_instance_create_instance(const launcher_services_api_v1* services,
                                       const LauncherInstanceManifest& desired_manifest,
                                       const std::string& state_root_override,
                                       LauncherInstanceManifest& out_created_manifest,
                                       LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time = get_time(services);
    std::string state_root;
    LauncherInstanceManifest m = desired_manifest;
    LauncherInstancePaths paths;
    std::vector<unsigned char> bytes;
    u64 after_hash64;

    if (!services || !fs || !time || !time->now_us) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "missing_services", 0ull, 0ull, "");
        return false;
    }
    if (m.instance_id.empty()) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "empty_instance_id", 0ull, 0ull, "");
        return false;
    }
    if (!launcher_is_safe_id_component(m.instance_id)) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "unsafe_instance_id", 0ull, 0ull, "");
        return false;
    }

    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "state_root_unavailable", 0ull, 0ull, "");
        return false;
    }

    m.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    if (m.creation_timestamp_us == 0ull) {
        m.creation_timestamp_us = time->now_us();
    }

    paths = launcher_instance_paths_make(state_root, m.instance_id);
    if (fs_file_exists(fs, paths.manifest_path)) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "manifest_exists", 0ull, 0ull,
                          std::string("state_root=") + state_root);
        return false;
    }

    if (!launcher_instance_ensure_root_layout(services, paths)) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "ensure_layout", 0ull, 0ull,
                          std::string("state_root=") + state_root);
        return false;
    }

    if (!launcher_instance_manifest_to_tlv_bytes(m, bytes)) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "encode_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root);
        return false;
    }
    if (!fs_write_all(fs, paths.staging_manifest_path, bytes)) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "write_staging_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root);
        return false;
    }
    if (std::rename(paths.staging_manifest_path.c_str(), paths.manifest_path.c_str()) != 0) {
        audit_instance_op(audit, "create_instance", m.instance_id, "fail", "commit_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root);
        return false;
    }

    out_created_manifest = m;
    after_hash64 = launcher_instance_manifest_hash64(m);
    audit_instance_op(audit,
                      "create_instance",
                      m.instance_id,
                      "ok",
                      "ok",
                      0ull,
                      after_hash64,
                      std::string("state_root=") + state_root + ";creation_timestamp_us=0x" + u64_hex16_string(m.creation_timestamp_us));
    return true;
}

bool launcher_instance_delete_instance(const launcher_services_api_v1* services,
                                       const std::string& instance_id,
                                       const std::string& state_root_override,
                                       LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time = get_time(services);
    std::string state_root;
    LauncherInstancePaths live_paths;
    LauncherInstancePaths tomb_paths;
    LauncherInstanceManifest live_manifest;
    u64 before_hash64;
    u64 stamp_us;
    char stamp_hex[17];

    if (!services || !fs || !time || !time->now_us) {
        audit_instance_op(audit, "delete_instance", instance_id, "fail", "missing_services", 0ull, 0ull, "");
        return false;
    }
    if (instance_id.empty()) {
        audit_instance_op(audit, "delete_instance", instance_id, "fail", "empty_instance_id", 0ull, 0ull, "");
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        audit_instance_op(audit, "delete_instance", instance_id, "fail", "unsafe_instance_id", 0ull, 0ull, "");
        return false;
    }

    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_instance_op(audit, "delete_instance", instance_id, "fail", "state_root_unavailable", 0ull, 0ull, "");
        return false;
    }

    live_paths = launcher_instance_paths_make(state_root, instance_id);
    if (!fs_file_exists(fs, live_paths.manifest_path)) {
        audit_instance_op(audit, "delete_instance", instance_id, "fail", "missing_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root);
        return false;
    }
    if (!launcher_instance_load_manifest(services, instance_id, state_root_override, live_manifest)) {
        audit_instance_op(audit, "delete_instance", instance_id, "fail", "read_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root);
        return false;
    }
    before_hash64 = launcher_instance_manifest_hash64(live_manifest);

    stamp_us = time->now_us();
    u64_to_hex16(stamp_us, stamp_hex);

    /* Create tombstone root as a sibling, then atomically swap names and move the live root into previous/. */
    {
        std::string tmp_tomb_id = instance_id + std::string(".__del_tomb_") + std::string(stamp_hex);
        std::string tmp_live_id = instance_id + std::string(".__del_live_") + std::string(stamp_hex);
        std::string tmp_live_root;
        std::string moved_root;

        tomb_paths = launcher_instance_paths_make(state_root, tmp_tomb_id);
        if (!launcher_instance_ensure_root_layout(services, tomb_paths)) {
            audit_instance_op(audit,
                              "delete_instance",
                              instance_id,
                              "fail",
                              "prepare_tombstone",
                              before_hash64,
                              0ull,
                              std::string("state_root=") + state_root + ";stamp_us=0x" + u64_hex16_string(stamp_us));
            return false;
        }

        tmp_live_root = path_join(live_paths.instances_root, tmp_live_id);

        if (std::rename(live_paths.instance_root.c_str(), tmp_live_root.c_str()) != 0) {
            audit_instance_op(audit,
                              "delete_instance",
                              instance_id,
                              "fail",
                              "rename_live_to_tmp",
                              before_hash64,
                              0ull,
                              std::string("state_root=") + state_root + ";stamp_us=0x" + u64_hex16_string(stamp_us));
            return false;
        }
        if (std::rename(tomb_paths.instance_root.c_str(), live_paths.instance_root.c_str()) != 0) {
            (void)std::rename(tmp_live_root.c_str(), live_paths.instance_root.c_str());
            audit_instance_op(audit,
                              "delete_instance",
                              instance_id,
                              "fail",
                              "swap_tombstone_into_place",
                              before_hash64,
                              0ull,
                              std::string("state_root=") + state_root + ";stamp_us=0x" + u64_hex16_string(stamp_us));
            return false;
        }

        moved_root = path_join(live_paths.previous_root, std::string("deleted_") + std::string(stamp_hex));
        if (std::rename(tmp_live_root.c_str(), moved_root.c_str()) != 0) {
            /* Roll back swap (best-effort). */
            (void)std::rename(live_paths.instance_root.c_str(), tomb_paths.instance_root.c_str());
            (void)std::rename(tmp_live_root.c_str(), live_paths.instance_root.c_str());
            audit_instance_op(audit,
                              "delete_instance",
                              instance_id,
                              "fail",
                              "move_into_previous",
                              before_hash64,
                              0ull,
                              std::string("state_root=") + state_root + ";stamp_us=0x" + u64_hex16_string(stamp_us));
            return false;
        }
    }

    audit_instance_op(audit,
                      "delete_instance",
                      instance_id,
                      "ok",
                      "ok",
                      before_hash64,
                      0ull,
                      std::string("state_root=") + state_root + ";stamp_us=0x" + u64_hex16_string(stamp_us));
    return true;
}

static bool create_from_source_manifest(const launcher_services_api_v1* services,
                                        const launcher_fs_api_v1* fs,
                                        const launcher_time_api_v1* time,
                                        const std::string& state_root,
                                        const std::string& source_instance_id,
                                        const std::string& new_instance_id,
                                        bool as_template,
                                        LauncherInstanceManifest& out_created_manifest,
                                        LauncherAuditLog* audit) {
    const std::string op = as_template ? std::string("template_instance") : std::string("clone_instance");
    LauncherInstanceManifest src;
    LauncherInstanceManifest m;
    LauncherInstancePaths src_paths;
    LauncherInstancePaths dst_paths;
    u64 src_hash64;
    u64 after_hash64;
    std::vector<unsigned char> bytes;

    if (!launcher_instance_load_manifest(services, source_instance_id, state_root, src)) {
        audit_instance_op(audit,
                          op,
                          new_instance_id,
                          "fail",
                          "read_source_manifest",
                          0ull,
                          0ull,
                          std::string("state_root=") + state_root + ";source_instance_id=" + source_instance_id);
        return false;
    }
    src_hash64 = launcher_instance_manifest_hash64(src);

    m = src;
    m.instance_id = new_instance_id;
    m.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    m.creation_timestamp_us = time->now_us();
    m.previous_manifest_hash64 = 0ull;
    m.provenance_source_instance_id = source_instance_id;
    m.provenance_source_manifest_hash64 = src_hash64;

    if (as_template) {
        size_t i;
        m.pinned_engine_build_id.clear();
        m.pinned_game_build_id.clear();
        m.known_good = 0u;
        m.last_verified_timestamp_us = 0ull;
        m.previous_manifest_hash64 = 0ull;
        for (i = 0u; i < m.content_entries.size(); ++i) {
            m.content_entries[i].hash_bytes.clear();
        }
    }

    after_hash64 = launcher_instance_manifest_hash64(m);

    dst_paths = launcher_instance_paths_make(state_root, new_instance_id);
    if (fs_file_exists(fs, dst_paths.manifest_path)) {
        audit_instance_op(audit,
                          op,
                          new_instance_id,
                          "fail",
                          "dest_manifest_exists",
                          src_hash64,
                          0ull,
                          std::string("state_root=") + state_root + ";source_instance_id=" + source_instance_id + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
        return false;
    }

    if (!launcher_instance_ensure_root_layout(services, dst_paths)) {
        audit_instance_op(audit,
                          op,
                          new_instance_id,
                          "fail",
                          "ensure_dest_layout",
                          src_hash64,
                          0ull,
                          std::string("state_root=") + state_root + ";source_instance_id=" + source_instance_id + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
        return false;
    }

    src_paths = launcher_instance_paths_make(state_root, source_instance_id);
    if (fs_file_exists(fs, src_paths.config_file_path)) {
        if (!fs_copy_file(fs, src_paths.config_file_path, dst_paths.config_file_path)) {
            audit_instance_op(audit,
                              op,
                              new_instance_id,
                              "fail",
                              "copy_config",
                              src_hash64,
                              0ull,
                              std::string("state_root=") + state_root + ";source_instance_id=" + source_instance_id + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
            return false;
        }
    }

    if (!launcher_instance_manifest_to_tlv_bytes(m, bytes)) {
        audit_instance_op(audit,
                          op,
                          new_instance_id,
                          "fail",
                          "encode_dest_manifest",
                          src_hash64,
                          0ull,
                          std::string("state_root=") + state_root + ";source_instance_id=" + source_instance_id + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
        return false;
    }
    if (!fs_write_all(fs, dst_paths.staging_manifest_path, bytes)) {
        audit_instance_op(audit,
                          op,
                          new_instance_id,
                          "fail",
                          "write_dest_staging_manifest",
                          src_hash64,
                          0ull,
                          std::string("state_root=") + state_root + ";source_instance_id=" + source_instance_id + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
        return false;
    }
    if (std::rename(dst_paths.staging_manifest_path.c_str(), dst_paths.manifest_path.c_str()) != 0) {
        audit_instance_op(audit,
                          op,
                          new_instance_id,
                          "fail",
                          "commit_dest_manifest",
                          src_hash64,
                          0ull,
                          std::string("state_root=") + state_root + ";source_instance_id=" + source_instance_id + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
        return false;
    }

    out_created_manifest = m;
    audit_instance_op(audit,
                      op,
                      new_instance_id,
                      "ok",
                      "ok",
                      src_hash64,
                      after_hash64,
                      std::string("state_root=") + state_root + ";source_instance_id=" + source_instance_id);
    return true;
}

bool launcher_instance_clone_instance(const launcher_services_api_v1* services,
                                      const std::string& source_instance_id,
                                      const std::string& new_instance_id,
                                      const std::string& state_root_override,
                                      LauncherInstanceManifest& out_created_manifest,
                                      LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time = get_time(services);
    std::string state_root;

    if (!services || !fs || !time || !time->now_us) {
        audit_instance_op(audit, "clone_instance", new_instance_id, "fail", "missing_services", 0ull, 0ull,
                          std::string("source_instance_id=") + source_instance_id);
        return false;
    }
    if (source_instance_id.empty() || new_instance_id.empty()) {
        audit_instance_op(audit, "clone_instance", new_instance_id, "fail", "empty_instance_id", 0ull, 0ull,
                          std::string("source_instance_id=") + source_instance_id);
        return false;
    }
    if (!launcher_is_safe_id_component(source_instance_id) || !launcher_is_safe_id_component(new_instance_id)) {
        audit_instance_op(audit, "clone_instance", new_instance_id, "fail", "unsafe_instance_id", 0ull, 0ull,
                          std::string("source_instance_id=") + source_instance_id);
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_instance_op(audit, "clone_instance", new_instance_id, "fail", "state_root_unavailable", 0ull, 0ull,
                          std::string("source_instance_id=") + source_instance_id);
        return false;
    }

    return create_from_source_manifest(services, fs, time, state_root, source_instance_id, new_instance_id,
                                       false, out_created_manifest, audit);
}

bool launcher_instance_template_instance(const launcher_services_api_v1* services,
                                         const std::string& source_instance_id,
                                         const std::string& new_instance_id,
                                         const std::string& state_root_override,
                                         LauncherInstanceManifest& out_created_manifest,
                                         LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time = get_time(services);
    std::string state_root;

    if (!services || !fs || !time || !time->now_us) {
        audit_instance_op(audit, "template_instance", new_instance_id, "fail", "missing_services", 0ull, 0ull,
                          std::string("source_instance_id=") + source_instance_id);
        return false;
    }
    if (source_instance_id.empty() || new_instance_id.empty()) {
        audit_instance_op(audit, "template_instance", new_instance_id, "fail", "empty_instance_id", 0ull, 0ull,
                          std::string("source_instance_id=") + source_instance_id);
        return false;
    }
    if (!launcher_is_safe_id_component(source_instance_id) || !launcher_is_safe_id_component(new_instance_id)) {
        audit_instance_op(audit, "template_instance", new_instance_id, "fail", "unsafe_instance_id", 0ull, 0ull,
                          std::string("source_instance_id=") + source_instance_id);
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_instance_op(audit, "template_instance", new_instance_id, "fail", "state_root_unavailable", 0ull, 0ull,
                          std::string("source_instance_id=") + source_instance_id);
        return false;
    }

    return create_from_source_manifest(services, fs, time, state_root, source_instance_id, new_instance_id,
                                       true, out_created_manifest, audit);
}

static bool update_manifest_marker(const launcher_services_api_v1* services,
                                  const launcher_fs_api_v1* fs,
                                  const launcher_time_api_v1* time,
                                  const std::string& state_root,
                                  const std::string& instance_id,
                                  bool mark_good,
                                  LauncherInstanceManifest& out_updated_manifest,
                                  LauncherAuditLog* audit) {
    const std::string op = mark_good ? std::string("mark_known_good") : std::string("mark_broken");
    LauncherInstanceManifest cur;
    LauncherInstanceManifest next;
    LauncherInstancePaths paths;
    std::vector<unsigned char> bytes;
    u64 before_hash64;
    u64 stamp_us;
    u64 after_hash64;

    if (!launcher_instance_load_manifest(services, instance_id, state_root, cur)) {
        audit_instance_op(audit, op, instance_id, "fail", "read_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root);
        return false;
    }
    before_hash64 = launcher_instance_manifest_hash64(cur);
    stamp_us = time->now_us();

    next = cur;
    next.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    next.previous_manifest_hash64 = before_hash64;
    next.known_good = mark_good ? 1u : 0u;
    if (mark_good) {
        next.last_verified_timestamp_us = stamp_us;
    }
    after_hash64 = launcher_instance_manifest_hash64(next);

    paths = launcher_instance_paths_make(state_root, instance_id);
    if (!launcher_instance_manifest_to_tlv_bytes(next, bytes)) {
        audit_instance_op(audit, op, instance_id, "fail", "encode_manifest", before_hash64, 0ull,
                          std::string("state_root=") + state_root + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
        return false;
    }
    if (!fs_write_all(fs, paths.staging_manifest_path, bytes)) {
        audit_instance_op(audit, op, instance_id, "fail", "write_staging_manifest", before_hash64, 0ull,
                          std::string("state_root=") + state_root + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
        return false;
    }

    if (!commit_manifest_with_previous(paths, before_hash64, stamp_us)) {
        audit_instance_op(audit, op, instance_id, "fail", "commit_manifest", before_hash64, 0ull,
                          std::string("state_root=") + state_root + ";stamp_us=0x" + u64_hex16_string(stamp_us) + ";planned_after_hash64=0x" + u64_hex16_string(after_hash64));
        return false;
    }

    out_updated_manifest = next;
    audit_instance_op(audit,
                      op,
                      instance_id,
                      "ok",
                      "ok",
                      before_hash64,
                      after_hash64,
                      std::string("state_root=") + state_root + ";stamp_us=0x" + u64_hex16_string(stamp_us));
    return true;
}

bool launcher_instance_mark_known_good(const launcher_services_api_v1* services,
                                       const std::string& instance_id,
                                       const std::string& state_root_override,
                                       LauncherInstanceManifest& out_updated_manifest,
                                       LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time = get_time(services);
    std::string state_root;

    if (!services || !fs || !time || !time->now_us) {
        audit_instance_op(audit, "mark_known_good", instance_id, "fail", "missing_services", 0ull, 0ull, "");
        return false;
    }
    if (instance_id.empty()) {
        audit_instance_op(audit, "mark_known_good", instance_id, "fail", "empty_instance_id", 0ull, 0ull, "");
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        audit_instance_op(audit, "mark_known_good", instance_id, "fail", "unsafe_instance_id", 0ull, 0ull, "");
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_instance_op(audit, "mark_known_good", instance_id, "fail", "state_root_unavailable", 0ull, 0ull, "");
        return false;
    }
    return update_manifest_marker(services, fs, time, state_root, instance_id, true, out_updated_manifest, audit);
}

bool launcher_instance_mark_broken(const launcher_services_api_v1* services,
                                   const std::string& instance_id,
                                   const std::string& state_root_override,
                                   LauncherInstanceManifest& out_updated_manifest,
                                   LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time = get_time(services);
    std::string state_root;

    if (!services || !fs || !time || !time->now_us) {
        audit_instance_op(audit, "mark_broken", instance_id, "fail", "missing_services", 0ull, 0ull, "");
        return false;
    }
    if (instance_id.empty()) {
        audit_instance_op(audit, "mark_broken", instance_id, "fail", "empty_instance_id", 0ull, 0ull, "");
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        audit_instance_op(audit, "mark_broken", instance_id, "fail", "unsafe_instance_id", 0ull, 0ull, "");
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_instance_op(audit, "mark_broken", instance_id, "fail", "state_root_unavailable", 0ull, 0ull, "");
        return false;
    }
    return update_manifest_marker(services, fs, time, state_root, instance_id, false, out_updated_manifest, audit);
}

bool launcher_instance_export_instance(const launcher_services_api_v1* services,
                                       const std::string& instance_id,
                                       const std::string& export_root,
                                       const std::string& state_root_override,
                                       u32 export_mode,
                                       LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    LauncherInstanceManifest m;
    LauncherInstancePaths src_paths;
    std::vector<unsigned char> manifest_bytes;
    std::string out_manifest_path;
    std::string out_config_root;
    std::string out_config_path;
    u64 hash64 = 0ull;

    if (!services || !fs) {
        audit_instance_op(audit, "export_instance", instance_id, "fail", "missing_services", 0ull, 0ull, "");
        return false;
    }
    if (instance_id.empty() || export_root.empty()) {
        audit_instance_op(audit, "export_instance", instance_id, "fail", "bad_args", 0ull, 0ull,
                          std::string("export_root=") + export_root);
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        audit_instance_op(audit, "export_instance", instance_id, "fail", "unsafe_instance_id", 0ull, 0ull,
                          std::string("export_root=") + export_root);
        return false;
    }
    if (export_mode != (u32)LAUNCHER_INSTANCE_EXPORT_DEFINITION_ONLY &&
        export_mode != (u32)LAUNCHER_INSTANCE_EXPORT_FULL_BUNDLE) {
        audit_instance_op(audit, "export_instance", instance_id, "fail", "bad_mode", 0ull, 0ull,
                          std::string("export_root=") + export_root);
        return false;
    }

    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_instance_op(audit, "export_instance", instance_id, "fail", "state_root_unavailable", 0ull, 0ull,
                          std::string("export_root=") + export_root);
        return false;
    }

    if (!launcher_instance_load_manifest(services, instance_id, state_root, m)) {
        audit_instance_op(audit, "export_instance", instance_id, "fail", "read_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root + ";export_root=" + export_root);
        return false;
    }
    hash64 = launcher_instance_manifest_hash64(m);

    src_paths = launcher_instance_paths_make(state_root, instance_id);
    if (!launcher_instance_manifest_to_tlv_bytes(m, manifest_bytes)) {
        audit_instance_op(audit, "export_instance", instance_id, "fail", "encode_manifest", hash64, hash64,
                          std::string("state_root=") + state_root + ";export_root=" + export_root);
        return false;
    }

    (void)mkdir_p_best_effort(export_root);
    out_manifest_path = path_join(export_root, "manifest.tlv");
    if (!fs_write_all(fs, out_manifest_path, manifest_bytes)) {
        audit_instance_op(audit, "export_instance", instance_id, "fail", "write_export_manifest", hash64, hash64,
                          std::string("state_root=") + state_root + ";export_root=" + export_root);
        return false;
    }

    out_config_root = path_join(export_root, "config");
    (void)mkdir_p_best_effort(out_config_root);
    out_config_path = path_join(out_config_root, "config.tlv");
    if (fs_file_exists(fs, src_paths.config_file_path)) {
        if (!fs_copy_file(fs, src_paths.config_file_path, out_config_path)) {
            audit_instance_op(audit, "export_instance", instance_id, "fail", "copy_export_config", hash64, hash64,
                              std::string("state_root=") + state_root + ";export_root=" + export_root);
            return false;
        }
    } else {
        if (!write_empty_config_file(fs, out_config_path)) {
            audit_instance_op(audit, "export_instance", instance_id, "fail", "write_export_config", hash64, hash64,
                              std::string("state_root=") + state_root + ";export_root=" + export_root);
            return false;
        }
    }

    if (export_mode == (u32)LAUNCHER_INSTANCE_EXPORT_FULL_BUNDLE) {
        std::string out_payloads_root = path_join(export_root, "payloads");
        size_t i;
        (void)mkdir_p_best_effort(out_payloads_root);
        for (i = 0u; i < m.content_entries.size(); ++i) {
            const LauncherContentEntry& e = m.content_entries[i];
            std::string hex = bytes_to_hex_lower(e.hash_bytes);
            std::string src_payload_path;
            std::string dst_payload_path;
            std::vector<unsigned char> payload;
            u64 fnv;

            if (e.hash_bytes.empty()) {
                continue;
            }
            src_payload_path = (e.type == (u32)LAUNCHER_CONTENT_MOD)
                                   ? path_join(src_paths.mods_root, hex + ".bin")
                                   : path_join(src_paths.content_root, hex + ".bin");
            if (!fs_file_exists(fs, src_payload_path)) {
                continue; /* optional payloads */
            }
            if (!fs_read_all(fs, src_payload_path, payload)) {
                audit_instance_op(audit, "export_instance", instance_id, "fail", "read_payload", hash64, hash64,
                                  std::string("state_root=") + state_root + ";export_root=" + export_root + ";payload_hex=" + hex);
                return false;
            }
            fnv = tlv_fnv1a64(payload.empty() ? (const unsigned char*)0 : &payload[0], payload.size());
            if (!hash_bytes_match_fnv64_le(e.hash_bytes, fnv)) {
                audit_instance_op(audit, "export_instance", instance_id, "fail", "payload_hash_mismatch", hash64, hash64,
                                  std::string("state_root=") + state_root + ";export_root=" + export_root + ";payload_hex=" + hex);
                return false;
            }
            dst_payload_path = path_join(out_payloads_root, hex + ".bin");
            if (!fs_write_all(fs, dst_payload_path, payload)) {
                audit_instance_op(audit, "export_instance", instance_id, "fail", "write_payload", hash64, hash64,
                                  std::string("state_root=") + state_root + ";export_root=" + export_root + ";payload_hex=" + hex);
                return false;
            }
        }
    }

    audit_instance_op(audit,
                      "export_instance",
                      instance_id,
                      "ok",
                      "ok",
                      hash64,
                      hash64,
                      std::string("state_root=") + state_root + ";export_root=" + export_root + ";mode=" +
                          std::string(export_mode == (u32)LAUNCHER_INSTANCE_EXPORT_DEFINITION_ONLY ? "definition" : "full"));
    return true;
}

bool launcher_instance_import_instance(const launcher_services_api_v1* services,
                                       const std::string& import_root,
                                       const std::string& new_instance_id,
                                       const std::string& state_root_override,
                                       u32 import_mode,
                                       u32 safe_mode,
                                       LauncherInstanceManifest& out_created_manifest,
                                       LauncherAuditLog* audit) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time = get_time(services);
    std::string state_root;
    std::string chosen_id = new_instance_id;
    std::string in_manifest_path;
    std::string in_config_path;
    std::vector<unsigned char> in_manifest_bytes;
    std::vector<unsigned char> in_config_bytes;
    LauncherInstanceManifest imported;
    LauncherInstanceManifest created;
    u64 imported_hash64 = 0ull;
    u64 created_hash64 = 0ull;
    LauncherInstancePaths dst_paths;

    if (!services || !fs || !time || !time->now_us) {
        audit_instance_op(audit, "import_instance", new_instance_id, "fail", "missing_services", 0ull, 0ull,
                          std::string("import_root=") + import_root);
        return false;
    }
    if (import_root.empty()) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "bad_args", 0ull, 0ull, "");
        return false;
    }
    if (import_mode != (u32)LAUNCHER_INSTANCE_IMPORT_DEFINITION_ONLY &&
        import_mode != (u32)LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "bad_mode", 0ull, 0ull,
                          std::string("import_root=") + import_root);
        return false;
    }

    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "state_root_unavailable", 0ull, 0ull,
                          std::string("import_root=") + import_root);
        return false;
    }

    if (chosen_id.empty()) {
        char hex[17];
        u64_to_hex16(time->now_us(), hex);
        chosen_id = std::string("inst_") + std::string(hex);
    }
    if (!launcher_is_safe_id_component(chosen_id)) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "unsafe_instance_id", 0ull, 0ull,
                          std::string("import_root=") + import_root);
        return false;
    }

    in_manifest_path = path_join(import_root, "manifest.tlv");
    if (!fs_read_all(fs, in_manifest_path, in_manifest_bytes) || in_manifest_bytes.empty()) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "read_import_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root + ";import_root=" + import_root);
        return false;
    }
    if (!launcher_instance_manifest_from_tlv_bytes(&in_manifest_bytes[0], in_manifest_bytes.size(), imported)) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "decode_import_manifest", 0ull, 0ull,
                          std::string("state_root=") + state_root + ";import_root=" + import_root);
        return false;
    }

    imported_hash64 = launcher_instance_manifest_hash64(imported);

    created = imported;
    created.instance_id = chosen_id;
    created.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
    created.creation_timestamp_us = time->now_us();
    created.known_good = 0u;
    created.last_verified_timestamp_us = 0ull;
    created.previous_manifest_hash64 = 0ull;
    created.provenance_source_instance_id = imported.instance_id;
    created.provenance_source_manifest_hash64 = imported_hash64;
    created_hash64 = launcher_instance_manifest_hash64(created);

    /* Optional config. */
    in_config_path = path_join(path_join(import_root, "config"), "config.tlv");
    if (fs_file_exists(fs, in_config_path)) {
        if (!fs_read_all(fs, in_config_path, in_config_bytes)) {
            audit_instance_op(audit, "import_instance", chosen_id, "fail", "read_import_config", imported_hash64, 0ull,
                              std::string("state_root=") + state_root + ";import_root=" + import_root + ";planned_after_hash64=0x" +
                                  u64_hex16_string(created_hash64));
            return false;
        }
    }

    /* Validate payloads (optional) before creating the destination instance. */
    if (import_mode == (u32)LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE) {
        size_t i;
        std::string payloads_root = path_join(import_root, "payloads");
        for (i = 0u; i < imported.content_entries.size(); ++i) {
            const LauncherContentEntry& e = imported.content_entries[i];
            std::string hex;
            std::string payload_path;
            std::vector<unsigned char> payload;
            u64 fnv;

            if (e.hash_bytes.empty()) {
                continue;
            }
            if (e.hash_bytes.size() != 8u) {
                if (!safe_mode) {
                    audit_instance_op(audit, "import_instance", chosen_id, "fail", "unsupported_payload_hash",
                                      imported_hash64, 0ull,
                                      std::string("state_root=") + state_root + ";import_root=" + import_root + ";planned_after_hash64=0x" +
                                          u64_hex16_string(created_hash64));
                    return false;
                }
                continue;
            }
            hex = bytes_to_hex_lower(e.hash_bytes);
            payload_path = path_join(payloads_root, hex + ".bin");
            if (!fs_file_exists(fs, payload_path)) {
                continue; /* optional */
            }
            if (!fs_read_all(fs, payload_path, payload)) {
                if (!safe_mode) {
                    audit_instance_op(audit, "import_instance", chosen_id, "fail", "read_payload",
                                      imported_hash64, 0ull,
                                      std::string("state_root=") + state_root + ";import_root=" + import_root + ";payload_hex=" + hex +
                                          ";planned_after_hash64=0x" + u64_hex16_string(created_hash64));
                    return false;
                }
                continue;
            }
            fnv = tlv_fnv1a64(payload.empty() ? (const unsigned char*)0 : &payload[0], payload.size());
            if (!hash_bytes_match_fnv64_le(e.hash_bytes, fnv)) {
                if (!safe_mode) {
                    audit_instance_op(audit, "import_instance", chosen_id, "fail", "payload_hash_mismatch",
                                      imported_hash64, 0ull,
                                      std::string("state_root=") + state_root + ";import_root=" + import_root + ";payload_hex=" + hex +
                                          ";planned_after_hash64=0x" + u64_hex16_string(created_hash64));
                    return false;
                }
            }
        }
    }

    dst_paths = launcher_instance_paths_make(state_root, chosen_id);
    if (fs_file_exists(fs, dst_paths.manifest_path)) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "dest_manifest_exists", imported_hash64, 0ull,
                          std::string("state_root=") + state_root + ";import_root=" + import_root + ";planned_after_hash64=0x" +
                              u64_hex16_string(created_hash64));
        return false;
    }
    if (!launcher_instance_ensure_root_layout(services, dst_paths)) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "ensure_dest_layout", imported_hash64, 0ull,
                          std::string("state_root=") + state_root + ";import_root=" + import_root + ";planned_after_hash64=0x" +
                              u64_hex16_string(created_hash64));
        return false;
    }

    if (!in_config_bytes.empty()) {
        if (!fs_write_all(fs, dst_paths.config_file_path, in_config_bytes)) {
            audit_instance_op(audit, "import_instance", chosen_id, "fail", "write_dest_config", imported_hash64, 0ull,
                              std::string("state_root=") + state_root + ";import_root=" + import_root + ";planned_after_hash64=0x" +
                                  u64_hex16_string(created_hash64));
            return false;
        }
    }

    if (import_mode == (u32)LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE) {
        size_t i;
        std::string payloads_root = path_join(import_root, "payloads");
        for (i = 0u; i < imported.content_entries.size(); ++i) {
            const LauncherContentEntry& e = imported.content_entries[i];
            std::string hex;
            std::string payload_path;
            std::string dst_path;

            if (e.hash_bytes.empty() || e.hash_bytes.size() != 8u) {
                continue;
            }
            hex = bytes_to_hex_lower(e.hash_bytes);
            payload_path = path_join(payloads_root, hex + ".bin");
            if (!fs_file_exists(fs, payload_path)) {
                continue;
            }
            dst_path = (e.type == (u32)LAUNCHER_CONTENT_MOD)
                           ? path_join(dst_paths.mods_root, hex + ".bin")
                           : path_join(dst_paths.content_root, hex + ".bin");
            if (!fs_copy_file(fs, payload_path, dst_path)) {
                if (!safe_mode) {
                    audit_instance_op(audit, "import_instance", chosen_id, "fail", "copy_payload",
                                      imported_hash64, 0ull,
                                      std::string("state_root=") + state_root + ";import_root=" + import_root + ";payload_hex=" + hex +
                                          ";planned_after_hash64=0x" + u64_hex16_string(created_hash64));
                    return false;
                }
            }
        }
    }

    if (!launcher_instance_manifest_to_tlv_bytes(created, in_manifest_bytes)) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "encode_dest_manifest",
                          imported_hash64, 0ull,
                          std::string("state_root=") + state_root + ";import_root=" + import_root + ";planned_after_hash64=0x" +
                              u64_hex16_string(created_hash64));
        return false;
    }
    if (!fs_write_all(fs, dst_paths.staging_manifest_path, in_manifest_bytes)) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "write_dest_staging_manifest",
                          imported_hash64, 0ull,
                          std::string("state_root=") + state_root + ";import_root=" + import_root + ";planned_after_hash64=0x" +
                              u64_hex16_string(created_hash64));
        return false;
    }
    if (std::rename(dst_paths.staging_manifest_path.c_str(), dst_paths.manifest_path.c_str()) != 0) {
        audit_instance_op(audit, "import_instance", chosen_id, "fail", "commit_dest_manifest",
                          imported_hash64, 0ull,
                          std::string("state_root=") + state_root + ";import_root=" + import_root + ";planned_after_hash64=0x" +
                              u64_hex16_string(created_hash64));
        return false;
    }

    out_created_manifest = created;
    audit_instance_op(audit,
                      "import_instance",
                      chosen_id,
                      "ok",
                      "ok",
                      imported_hash64,
                      created_hash64,
                      std::string("state_root=") + state_root + ";import_root=" + import_root + ";mode=" +
                          std::string(import_mode == (u32)LAUNCHER_INSTANCE_IMPORT_DEFINITION_ONLY ? "definition" : "full") +
                          ";safe_mode=" + std::string(safe_mode ? "1" : "0") +
                          ";source_instance_id=" + imported.instance_id);
    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
