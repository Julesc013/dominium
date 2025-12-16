/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance_config.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_config
RESPONSIBILITY: Implements instance config TLV encode/decode (skip-unknown; deterministic).
*/

#include "launcher_instance_config.h"

#include <cstdio>

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

static LauncherDomainOverride decode_domain_override(const unsigned char* data, size_t size) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherDomainOverride d;

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_INSTANCE_CONFIG_DOMAIN_TLV_TAG_DOMAIN_KEY:
            d.domain_key = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_INSTANCE_CONFIG_DOMAIN_TLV_TAG_ENABLED: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                d.enabled = v ? 1u : 0u;
            }
            break;
        }
        default:
            tlv_unknown_capture(d.unknown_fields, rec);
            break;
        }
    }
    return d;
}

static void encode_domain_override(TlvWriter& w, const LauncherDomainOverride& d) {
    TlvWriter inner;
    inner.add_string(LAUNCHER_INSTANCE_CONFIG_DOMAIN_TLV_TAG_DOMAIN_KEY, d.domain_key);
    inner.add_u32(LAUNCHER_INSTANCE_CONFIG_DOMAIN_TLV_TAG_ENABLED, d.enabled ? 1u : 0u);
    tlv_unknown_emit(inner, d.unknown_fields);
    w.add_container(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_DOMAIN_OVERRIDE, inner.bytes());
}

} /* namespace */

LauncherDomainOverride::LauncherDomainOverride()
    : domain_key(), enabled(0u), unknown_fields() {
}

LauncherInstanceConfig::LauncherInstanceConfig()
    : schema_version(LAUNCHER_INSTANCE_CONFIG_TLV_VERSION),
      instance_id(),
      gfx_backend(),
      renderer_api(),
      window_mode(LAUNCHER_WINDOW_MODE_AUTO),
      window_width(0u),
      window_height(0u),
      window_dpi(0u),
      window_monitor(0u),
      audio_device_id(),
      input_backend(),
      allow_network(1u),
      debug_flags(0u),
      domain_overrides(),
      auto_recovery_failure_threshold(3u),
      launch_history_max_entries(10u),
      unknown_fields() {
}

LauncherInstanceConfig launcher_instance_config_make_default(const std::string& instance_id) {
    LauncherInstanceConfig c;
    c.instance_id = instance_id;
    return c;
}

bool launcher_instance_config_to_tlv_bytes(const LauncherInstanceConfig& cfg,
                                           std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_INSTANCE_CONFIG_TLV_VERSION);
    w.add_string(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_INSTANCE_ID, cfg.instance_id);

    if (!cfg.gfx_backend.empty()) {
        w.add_string(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_GFX_BACKEND, cfg.gfx_backend);
    }
    if (!cfg.renderer_api.empty()) {
        w.add_string(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_RENDERER_API, cfg.renderer_api);
    }

    if (cfg.window_mode != LAUNCHER_WINDOW_MODE_AUTO) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_MODE, cfg.window_mode);
    }
    if (cfg.window_width != 0u) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_WIDTH, cfg.window_width);
    }
    if (cfg.window_height != 0u) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_HEIGHT, cfg.window_height);
    }
    if (cfg.window_dpi != 0u) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_DPI, cfg.window_dpi);
    }
    if (cfg.window_monitor != 0u) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_MONITOR, cfg.window_monitor);
    }

    if (!cfg.audio_device_id.empty()) {
        w.add_string(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_AUDIO_DEVICE_ID, cfg.audio_device_id);
    }
    if (!cfg.input_backend.empty()) {
        w.add_string(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_INPUT_BACKEND, cfg.input_backend);
    }

    if (cfg.allow_network == 0u) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_ALLOW_NETWORK, 0u);
    }
    if (cfg.debug_flags != 0u) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_DEBUG_FLAGS, cfg.debug_flags);
    }

    if (cfg.auto_recovery_failure_threshold != 0u && cfg.auto_recovery_failure_threshold != 3u) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_AUTO_RECOVERY_THRESHOLD, cfg.auto_recovery_failure_threshold);
    }
    if (cfg.launch_history_max_entries != 0u && cfg.launch_history_max_entries != 10u) {
        w.add_u32(LAUNCHER_INSTANCE_CONFIG_TLV_TAG_LAUNCH_HISTORY_MAX_ENTRIES, cfg.launch_history_max_entries);
    }

    for (i = 0u; i < cfg.domain_overrides.size(); ++i) {
        encode_domain_override(w, cfg.domain_overrides[i]);
    }

    tlv_unknown_emit(w, cfg.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

bool launcher_instance_config_from_tlv_bytes(const unsigned char* data,
                                             size_t size,
                                             LauncherInstanceConfig& out_cfg) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;
    LauncherInstanceConfig cfg;

    if (!data || size == 0u) {
        return false;
    }
    if (!tlv_read_schema_version_or_default(data, size, version, 1u)) {
        return false;
    }
    cfg.schema_version = version;

    while (r.next(rec)) {
        if (rec.tag == LAUNCHER_TLV_TAG_SCHEMA_VERSION) {
            continue;
        }
        switch (rec.tag) {
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_INSTANCE_ID:
            cfg.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_GFX_BACKEND:
            cfg.gfx_backend = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_RENDERER_API:
            cfg.renderer_api = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_MODE: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.window_mode = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_WIDTH: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.window_width = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_HEIGHT: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.window_height = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_DPI: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.window_dpi = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_MONITOR: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.window_monitor = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_AUDIO_DEVICE_ID:
            cfg.audio_device_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_INPUT_BACKEND:
            cfg.input_backend = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_ALLOW_NETWORK: {
            u32 v = 1u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.allow_network = v ? 1u : 0u;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_DEBUG_FLAGS: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.debug_flags = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_AUTO_RECOVERY_THRESHOLD: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.auto_recovery_failure_threshold = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_LAUNCH_HISTORY_MAX_ENTRIES: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                cfg.launch_history_max_entries = v;
            }
            break;
        }
        case LAUNCHER_INSTANCE_CONFIG_TLV_TAG_DOMAIN_OVERRIDE: {
            LauncherDomainOverride d = decode_domain_override(rec.payload, (size_t)rec.len);
            if (!d.domain_key.empty()) {
                cfg.domain_overrides.push_back(d);
            }
            break;
        }
        default:
            tlv_unknown_capture(cfg.unknown_fields, rec);
            break;
        }
    }

    if (cfg.allow_network != 0u) {
        cfg.allow_network = 1u;
    }
    if (cfg.auto_recovery_failure_threshold == 0u) {
        cfg.auto_recovery_failure_threshold = 3u;
    }
    if (cfg.launch_history_max_entries == 0u) {
        cfg.launch_history_max_entries = 10u;
    }
    out_cfg = cfg;
    return true;
}

bool launcher_instance_config_load(const launcher_services_api_v1* services,
                                   const LauncherInstancePaths& paths,
                                   LauncherInstanceConfig& out_cfg) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::vector<unsigned char> bytes;
    LauncherInstanceConfig cfg;

    if (!fs) {
        return false;
    }
    if (!fs_read_all(fs, paths.config_file_path, bytes)) {
        out_cfg = launcher_instance_config_make_default(std::string());
        return true;
    }
    if (bytes.empty()) {
        out_cfg = launcher_instance_config_make_default(std::string());
        return true;
    }
    if (!launcher_instance_config_from_tlv_bytes(&bytes[0], bytes.size(), cfg)) {
        return false;
    }
    out_cfg = cfg;
    return true;
}

bool launcher_instance_config_store(const launcher_services_api_v1* services,
                                    const LauncherInstancePaths& paths,
                                    const LauncherInstanceConfig& cfg) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::vector<unsigned char> bytes;
    if (!fs) {
        return false;
    }
    if (!launcher_instance_config_to_tlv_bytes(cfg, bytes)) {
        return false;
    }
    return fs_write_all_atomic(fs, paths.config_file_path, bytes);
}

} /* namespace launcher_core */
} /* namespace dom */
