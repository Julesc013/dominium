/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance_launch_history.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_launch_history
RESPONSIBILITY: Implements launch attempt history TLV encode/decode + filesystem helpers (skip-unknown; deterministic).
*/

#include "launcher_instance_launch_history.h"

#include <cstdio>

#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

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

static bool fs_read_all(const launcher_fs_api_v1* fs, const std::string& path, std::vector<unsigned char>& out_bytes) {
    void* fh;
    long sz;
    size_t got;

    out_bytes.clear();
    if (!fs || !fs->file_open || !fs->file_close || !fs->file_read || !fs->file_seek || !fs->file_tell) {
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

static bool fs_write_all(const launcher_fs_api_v1* fs, const std::string& path, const std::vector<unsigned char>& bytes) {
    void* fh;
    size_t wrote;

    if (!fs || !fs->file_open || !fs->file_close || !fs->file_write) {
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
    if (!path.empty()) {
        (void)std::remove(path.c_str());
    }
}

static bool fs_write_all_atomic(const launcher_fs_api_v1* fs,
                                const std::string& path,
                                const std::vector<unsigned char>& bytes) {
    const std::string tmp = path + ".tmp";
    const std::string bak = path + ".bak";

    remove_file_best_effort(tmp);
    if (!fs_write_all(fs, tmp, bytes)) {
        remove_file_best_effort(tmp);
        return false;
    }

    if (fs_file_exists(fs, path)) {
        remove_file_best_effort(bak);
        if (std::rename(path.c_str(), bak.c_str()) != 0) {
            remove_file_best_effort(tmp);
            return false;
        }
    }
    if (std::rename(tmp.c_str(), path.c_str()) != 0) {
        if (fs_file_exists(fs, bak)) {
            (void)std::rename(bak.c_str(), path.c_str());
        }
        remove_file_best_effort(tmp);
        return false;
    }
    remove_file_best_effort(bak);
    return true;
}

static void tlv_unknown_capture(std::vector<LauncherTlvUnknownRecord>& dst, const TlvRecord& rec) {
    LauncherTlvUnknownRecord u;
    u.tag = rec.tag;
    u.payload.clear();
    if (rec.len > 0u && rec.payload) {
        u.payload.assign(rec.payload, rec.payload + (size_t)rec.len);
    }
    dst.push_back(u);
}

static void tlv_unknown_emit(TlvWriter& w, const std::vector<LauncherTlvUnknownRecord>& src) {
    size_t i;
    for (i = 0u; i < src.size(); ++i) {
        if (!src[i].payload.empty()) {
            w.add_bytes(src[i].tag, &src[i].payload[0], (u32)src[i].payload.size());
        } else {
            w.add_bytes(src[i].tag, (const unsigned char*)0, 0u);
        }
    }
}

static LauncherInstanceLaunchAttempt decode_attempt(const unsigned char* data, size_t size) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherInstanceLaunchAttempt a;

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_TIMESTAMP_US: {
            u64 v = 0ull;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                a.timestamp_us = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_MANIFEST_HASH64: {
            u64 v = 0ull;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                a.manifest_hash64 = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_CONFIG_HASH64: {
            u64 v = 0ull;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                a.config_hash64 = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_SAFE_MODE: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                a.safe_mode = v ? 1u : 0u;
            }
            break;
        }
        case LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_OUTCOME: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                a.outcome = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_EXIT_CODE: {
            i32 v = 0;
            if (tlv_read_i32_le(rec.payload, rec.len, v)) {
                a.exit_code = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_DETAIL:
            a.detail = tlv_read_string(rec.payload, rec.len);
            break;
        default:
            tlv_unknown_capture(a.unknown_fields, rec);
            break;
        }
    }

    return a;
}

static void encode_attempt(TlvWriter& w, const LauncherInstanceLaunchAttempt& a) {
    TlvWriter inner;
    inner.add_u64(LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_TIMESTAMP_US, a.timestamp_us);
    inner.add_u64(LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_MANIFEST_HASH64, a.manifest_hash64);
    inner.add_u64(LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_CONFIG_HASH64, a.config_hash64);
    inner.add_u32(LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_SAFE_MODE, a.safe_mode ? 1u : 0u);
    inner.add_u32(LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_OUTCOME, a.outcome);
    if (a.outcome == (u32)LAUNCHER_LAUNCH_OUTCOME_CRASH) {
        inner.add_i32(LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_EXIT_CODE, a.exit_code);
    }
    if (!a.detail.empty()) {
        inner.add_string(LAUNCHER_INSTANCE_LAUNCH_ATTEMPT_TLV_TAG_DETAIL, a.detail);
    }
    tlv_unknown_emit(inner, a.unknown_fields);
    w.add_container(LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_ATTEMPT, inner.bytes());
}

} /* namespace */

LauncherInstanceLaunchAttempt::LauncherInstanceLaunchAttempt()
    : timestamp_us(0ull),
      manifest_hash64(0ull),
      config_hash64(0ull),
      safe_mode(0u),
      outcome((u32)LAUNCHER_LAUNCH_OUTCOME_SUCCESS),
      exit_code(0),
      detail(),
      unknown_fields() {
}

LauncherInstanceLaunchHistory::LauncherInstanceLaunchHistory()
    : schema_version(LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_VERSION),
      instance_id(),
      max_entries(10u),
      attempts(),
      unknown_fields() {
}

LauncherInstanceLaunchHistory launcher_instance_launch_history_make_default(const std::string& instance_id,
                                                                            u32 max_entries) {
    LauncherInstanceLaunchHistory h;
    h.instance_id = instance_id;
    h.max_entries = (max_entries == 0u) ? 10u : max_entries;
    return h;
}

bool launcher_instance_launch_history_to_tlv_bytes(const LauncherInstanceLaunchHistory& h,
                                                   std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_VERSION);
    w.add_string(LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_INSTANCE_ID, h.instance_id);
    w.add_u32(LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_MAX_ENTRIES, h.max_entries == 0u ? 10u : h.max_entries);
    for (i = 0u; i < h.attempts.size(); ++i) {
        encode_attempt(w, h.attempts[i]);
    }
    tlv_unknown_emit(w, h.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

bool launcher_instance_launch_history_from_tlv_bytes(const unsigned char* data,
                                                     size_t size,
                                                     LauncherInstanceLaunchHistory& out_h) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;
    LauncherInstanceLaunchHistory h;

    if (!data || size == 0u) {
        return false;
    }
    if (!tlv_read_schema_version_or_default(data, size, version, 1u)) {
        return false;
    }
    h.schema_version = version;

    while (r.next(rec)) {
        if (rec.tag == LAUNCHER_TLV_TAG_SCHEMA_VERSION) {
            continue;
        }
        switch (rec.tag) {
        case LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_INSTANCE_ID:
            h.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_MAX_ENTRIES: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                h.max_entries = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_TAG_ATTEMPT: {
            LauncherInstanceLaunchAttempt a = decode_attempt(rec.payload, (size_t)rec.len);
            h.attempts.push_back(a);
            break;
        }
        default:
            tlv_unknown_capture(h.unknown_fields, rec);
            break;
        }
    }

    if (h.max_entries == 0u) {
        h.max_entries = 10u;
    }
    out_h = h;
    return true;
}

std::string launcher_instance_launch_history_path(const LauncherInstancePaths& paths) {
    return path_join(paths.logs_root, "launch_history.tlv");
}

bool launcher_instance_launch_history_load(const launcher_services_api_v1* services,
                                           const LauncherInstancePaths& paths,
                                           LauncherInstanceLaunchHistory& out_h) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const std::string path = launcher_instance_launch_history_path(paths);
    std::vector<unsigned char> bytes;
    LauncherInstanceLaunchHistory h;

    if (!fs) {
        return false;
    }
    if (!fs_read_all(fs, path, bytes)) {
        out_h = launcher_instance_launch_history_make_default(std::string(), 10u);
        return true;
    }
    if (!launcher_instance_launch_history_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), h)) {
        return false;
    }
    out_h = h;
    return true;
}

bool launcher_instance_launch_history_store(const launcher_services_api_v1* services,
                                            const LauncherInstancePaths& paths,
                                            const LauncherInstanceLaunchHistory& h) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const std::string path = launcher_instance_launch_history_path(paths);
    std::vector<unsigned char> bytes;
    if (!fs) {
        return false;
    }
    if (!launcher_instance_launch_history_to_tlv_bytes(h, bytes)) {
        return false;
    }
    return fs_write_all_atomic(fs, path, bytes);
}

void launcher_instance_launch_history_append(LauncherInstanceLaunchHistory& h,
                                             const LauncherInstanceLaunchAttempt& attempt) {
    const u32 max_entries = (h.max_entries == 0u) ? 10u : h.max_entries;
    h.attempts.push_back(attempt);
    while (h.attempts.size() > (size_t)max_entries) {
        h.attempts.erase(h.attempts.begin());
    }
}

} /* namespace launcher_core */
} /* namespace dom */
