/*
FILE: source/dominium/launcher/core/src/artifact/launcher_artifact_store.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / artifact_store
RESPONSIBILITY: Implements artifact store metadata TLV and read-only verification (sha256).
*/

#include "launcher_artifact_store.h"

#include <cstdio>
#include <cstring>

#include "launcher_log.h"
#include "launcher_sha256.h"
#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"

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

static bool hash_bytes_equal(const std::vector<unsigned char>& a, const std::vector<unsigned char>& b) {
    size_t i;
    if (a.size() != b.size()) {
        return false;
    }
    for (i = 0u; i < a.size(); ++i) {
        if (a[i] != b[i]) {
            return false;
        }
    }
    return true;
}

static void emit_artifact_event(const launcher_services_api_v1* services,
                                const std::string& state_root_override,
                                u32 event_code,
                                const err_t* err) {
    core_log_event ev;
    core_log_scope scope;

    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_ARTIFACT;
    ev.code = (u16)event_code;
    ev.severity = (u8)((event_code == CORE_LOG_EVT_OP_FAIL) ? CORE_LOG_SEV_ERROR : CORE_LOG_SEV_INFO);
    ev.msg_id = 0u;
    ev.t_mono = 0u;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_OPERATION_ID, CORE_LOG_OP_LAUNCHER_ARTIFACT_VERIFY);
    if (err && !err_is_ok(err)) {
        launcher_log_add_err_fields(&ev, err);
    }

    std::memset(&scope, 0, sizeof(scope));
    scope.kind = CORE_LOG_SCOPE_GLOBAL;
    scope.state_root = state_root_override.empty() ? (const char*)0 : state_root_override.c_str();
    (void)launcher_services_emit_event(services, &scope, &ev);
}

} /* namespace */

LauncherArtifactMetadata::LauncherArtifactMetadata()
    : schema_version(LAUNCHER_ARTIFACT_METADATA_TLV_VERSION),
      hash_bytes(),
      size_bytes(0ull),
      content_type((u32)LAUNCHER_CONTENT_UNKNOWN),
      timestamp_us(0ull),
      verification_status((u32)LAUNCHER_ARTIFACT_VERIFY_UNKNOWN),
      source(),
      unknown_fields() {
}

bool launcher_artifact_metadata_to_tlv_bytes(const LauncherArtifactMetadata& meta,
                                             std::vector<unsigned char>& out_bytes) {
    TlvWriter w;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_ARTIFACT_METADATA_TLV_VERSION);
    if (!meta.hash_bytes.empty()) {
        w.add_bytes(LAUNCHER_ARTIFACT_TLV_TAG_HASH_BYTES, &meta.hash_bytes[0], (u32)meta.hash_bytes.size());
    } else {
        w.add_bytes(LAUNCHER_ARTIFACT_TLV_TAG_HASH_BYTES, (const unsigned char*)0, 0u);
    }
    w.add_u64(LAUNCHER_ARTIFACT_TLV_TAG_SIZE_BYTES, meta.size_bytes);
    w.add_u32(LAUNCHER_ARTIFACT_TLV_TAG_CONTENT_TYPE, meta.content_type);
    w.add_u64(LAUNCHER_ARTIFACT_TLV_TAG_TIMESTAMP_US, meta.timestamp_us);
    w.add_u32(LAUNCHER_ARTIFACT_TLV_TAG_VERIFICATION_STATUS, meta.verification_status);
    if (!meta.source.empty()) {
        w.add_string(LAUNCHER_ARTIFACT_TLV_TAG_SOURCE, meta.source);
    }

    tlv_unknown_emit(w, meta.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

bool launcher_artifact_metadata_from_tlv_bytes(const unsigned char* data,
                                               size_t size,
                                               LauncherArtifactMetadata& out_meta) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;
    LauncherArtifactMetadata m;

    if (!data || size == 0u) {
        return false;
    }

    if (!tlv_read_schema_version_or_default(data,
                                            size,
                                            version,
                                            launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_ARTIFACT_METADATA))) {
        return false;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_ARTIFACT_METADATA, version)) {
        return false;
    }
    m.schema_version = launcher_tlv_schema_current_version(LAUNCHER_TLV_SCHEMA_ARTIFACT_METADATA);

    while (r.next(rec)) {
        if (rec.tag == LAUNCHER_TLV_TAG_SCHEMA_VERSION) {
            continue;
        }
        switch (rec.tag) {
        case LAUNCHER_ARTIFACT_TLV_TAG_HASH_BYTES:
            m.hash_bytes.clear();
            if (rec.len > 0u && rec.payload) {
                m.hash_bytes.assign(rec.payload, rec.payload + (size_t)rec.len);
            }
            break;
        case LAUNCHER_ARTIFACT_TLV_TAG_SIZE_BYTES: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                m.size_bytes = v;
            }
            break;
        }
        case LAUNCHER_ARTIFACT_TLV_TAG_CONTENT_TYPE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                m.content_type = v;
            }
            break;
        }
        case LAUNCHER_ARTIFACT_TLV_TAG_TIMESTAMP_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                m.timestamp_us = v;
            }
            break;
        }
        case LAUNCHER_ARTIFACT_TLV_TAG_VERIFICATION_STATUS: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                m.verification_status = v;
            }
            break;
        }
        case LAUNCHER_ARTIFACT_TLV_TAG_SOURCE:
            m.source = tlv_read_string(rec.payload, rec.len);
            break;
        default:
            tlv_unknown_capture(m.unknown_fields, rec);
            break;
        }
    }

    out_meta = m;
    return true;
}

const char* launcher_artifact_store_default_algo(void) {
    return "sha256";
}

const char* launcher_artifact_store_payload_filename(void) {
    return "payload.bin";
}

bool launcher_artifact_store_paths(const std::string& state_root,
                                   const std::vector<unsigned char>& hash_bytes,
                                   std::string& out_artifact_dir,
                                   std::string& out_metadata_path,
                                   std::string& out_payload_path) {
    std::string algo;
    std::string hex;
    if (state_root.empty()) {
        return false;
    }
    if (hash_bytes.empty()) {
        return false;
    }
    algo = std::string(launcher_artifact_store_default_algo());
    hex = bytes_to_hex_lower(hash_bytes);
    out_artifact_dir = path_join(path_join(path_join(state_root, "artifacts"), algo), hex);
    out_metadata_path = path_join(out_artifact_dir, "artifact.tlv");
    out_payload_path = path_join(path_join(out_artifact_dir, "payload"), launcher_artifact_store_payload_filename());
    return true;
}

bool launcher_artifact_store_read_metadata(const launcher_services_api_v1* services,
                                           const std::string& state_root_override,
                                           const std::vector<unsigned char>& hash_bytes,
                                           LauncherArtifactMetadata& out_meta) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    std::vector<unsigned char> bytes;

    if (!services || !fs) {
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        return false;
    }
    if (!launcher_artifact_store_paths(state_root, hash_bytes, dir, meta_path, payload_path)) {
        return false;
    }
    if (!fs_read_all(fs, meta_path, bytes)) {
        return false;
    }
    if (!launcher_artifact_metadata_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), out_meta)) {
        return false;
    }
    return true;
}

bool launcher_artifact_store_read_metadata_ex(const launcher_services_api_v1* services,
                                              const std::string& state_root_override,
                                              const std::vector<unsigned char>& hash_bytes,
                                              LauncherArtifactMetadata& out_meta,
                                              err_t* out_err) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    std::vector<unsigned char> bytes;
    err_t err = err_ok();

    if (!services || !fs) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        goto fail;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_STATE_ROOT_UNAVAILABLE, 0u, (u32)ERRMSG_LAUNCHER_STATE_ROOT_UNAVAILABLE);
        goto fail;
    }
    if (!launcher_artifact_store_paths(state_root, hash_bytes, dir, meta_path, payload_path)) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
        goto fail;
    }
    if (!fs_read_all(fs, meta_path, bytes)) {
        err = err_make((u16)ERRD_ARTIFACT, (u16)ERRC_ARTIFACT_METADATA_NOT_FOUND, 0u, (u32)ERRMSG_ARTIFACT_METADATA_NOT_FOUND);
        goto fail;
    }
    if (!launcher_artifact_metadata_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), out_meta)) {
        err = err_make((u16)ERRD_ARTIFACT, (u16)ERRC_ARTIFACT_METADATA_INVALID, (u32)ERRF_INTEGRITY,
                       (u32)ERRMSG_ARTIFACT_METADATA_INVALID);
        goto fail;
    }
    if (out_err) {
        *out_err = err_ok();
    }
    return true;
fail:
    if (out_err) {
        *out_err = err;
    }
    return false;
}

bool launcher_artifact_store_verify(const launcher_services_api_v1* services,
                                    const std::string& state_root_override,
                                    const std::vector<unsigned char>& expected_hash_bytes,
                                    u32 expected_content_type,
                                    LauncherArtifactMetadata& out_meta) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    std::vector<unsigned char> payload_hash;
    u64 payload_size = 0ull;
    LauncherArtifactMetadata meta;

    if (!services || !fs) {
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        return false;
    }
    if (!launcher_artifact_store_paths(state_root, expected_hash_bytes, dir, meta_path, payload_path)) {
        return false;
    }
    if (!launcher_artifact_store_read_metadata(services, state_root, expected_hash_bytes, meta)) {
        return false;
    }
    if (!hash_bytes_equal(meta.hash_bytes, expected_hash_bytes)) {
        return false;
    }
    if (expected_content_type != (u32)LAUNCHER_CONTENT_UNKNOWN) {
        if (meta.content_type != expected_content_type) {
            return false;
        }
    }
    if (!launcher_sha256_file(services, payload_path, payload_hash, payload_size)) {
        return false;
    }
    if (!hash_bytes_equal(payload_hash, expected_hash_bytes)) {
        return false;
    }
    if (meta.size_bytes != 0ull && meta.size_bytes != payload_size) {
        return false;
    }

    out_meta = meta;
    return true;
}

bool launcher_artifact_store_verify_ex(const launcher_services_api_v1* services,
                                       const std::string& state_root_override,
                                       const std::vector<unsigned char>& expected_hash_bytes,
                                       u32 expected_content_type,
                                       LauncherArtifactMetadata& out_meta,
                                       err_t* out_err) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    std::vector<unsigned char> payload_hash;
    u64 payload_size = 0ull;
    LauncherArtifactMetadata meta;
    err_t err = err_ok();

    if (!services || !fs) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        goto fail;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_STATE_ROOT_UNAVAILABLE, 0u, (u32)ERRMSG_LAUNCHER_STATE_ROOT_UNAVAILABLE);
        goto fail;
    }
    if (!launcher_artifact_store_paths(state_root, expected_hash_bytes, dir, meta_path, payload_path)) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
        goto fail;
    }
    if (!launcher_artifact_store_read_metadata_ex(services, state_root, expected_hash_bytes, meta, &err)) {
        goto fail;
    }
    if (!hash_bytes_equal(meta.hash_bytes, expected_hash_bytes)) {
        err = err_make((u16)ERRD_ARTIFACT, (u16)ERRC_ARTIFACT_METADATA_INVALID, (u32)ERRF_INTEGRITY,
                       (u32)ERRMSG_ARTIFACT_METADATA_INVALID);
        goto fail;
    }
    if (expected_content_type != (u32)LAUNCHER_CONTENT_UNKNOWN && meta.content_type != expected_content_type) {
        err = err_make((u16)ERRD_ARTIFACT, (u16)ERRC_ARTIFACT_CONTENT_TYPE_MISMATCH, (u32)ERRF_INTEGRITY,
                       (u32)ERRMSG_ARTIFACT_CONTENT_TYPE_MISMATCH);
        goto fail;
    }
    if (!launcher_sha256_file(services, payload_path, payload_hash, payload_size)) {
        err = err_make((u16)ERRD_ARTIFACT, (u16)ERRC_ARTIFACT_PAYLOAD_MISSING, 0u, (u32)ERRMSG_ARTIFACT_PAYLOAD_MISSING);
        goto fail;
    }
    if (!hash_bytes_equal(payload_hash, expected_hash_bytes)) {
        err = err_make((u16)ERRD_ARTIFACT, (u16)ERRC_ARTIFACT_PAYLOAD_HASH_MISMATCH, (u32)ERRF_INTEGRITY,
                       (u32)ERRMSG_ARTIFACT_PAYLOAD_HASH_MISMATCH);
        goto fail;
    }
    if (meta.size_bytes != 0ull && meta.size_bytes != payload_size) {
        err = err_make((u16)ERRD_ARTIFACT, (u16)ERRC_ARTIFACT_SIZE_MISMATCH, (u32)ERRF_INTEGRITY,
                       (u32)ERRMSG_ARTIFACT_SIZE_MISMATCH);
        goto fail;
    }

    out_meta = meta;
    if (out_err) {
        *out_err = err_ok();
    }
    emit_artifact_event(services, state_root_override, CORE_LOG_EVT_OP_OK, (const err_t*)0);
    return true;
fail:
    if (out_err) {
        *out_err = err;
    }
    emit_artifact_event(services, state_root_override, CORE_LOG_EVT_OP_FAIL, &err);
    return false;
}

} /* namespace launcher_core */
} /* namespace dom */
