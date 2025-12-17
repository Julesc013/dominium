/*
FILE: source/dominium/launcher/core/src/launch/launcher_prelaunch.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / prelaunch
RESPONSIBILITY: Implements deterministic pre-launch config resolution, safe mode selection, and validation.
*/

#include "launcher_prelaunch.h"

#include <cstdio>
#include <cstring>

#include "launcher_audit.h"
#include "launcher_artifact_store.h"
#include "launcher_instance_known_good.h"
#include "launcher_instance_ops.h"
#include "launcher_pack_resolver.h"
#include "launcher_safety.h"
#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

static void audit_reason(LauncherAuditLog* audit, const std::string& r) {
    if (!audit) {
        return;
    }
    audit->reasons.push_back(r);
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

static bool get_state_root(const launcher_fs_api_v1* fs, std::string& out_state_root) {
    char buf[260];
    std::memset(buf, 0, sizeof(buf));
    out_state_root.clear();
    if (!fs || !fs->get_path) {
        return false;
    }
    if (!fs->get_path(LAUNCHER_FS_PATH_STATE, buf, sizeof(buf))) {
        return false;
    }
    if (!buf[0]) {
        return false;
    }
    out_state_root = buf;
    return true;
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

static bool fs_write_probe(const launcher_fs_api_v1* fs, const std::string& path) {
    void* fh;
    if (!fs || !fs->file_open || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "wb");
    if (!fh) {
        return false;
    }
    (void)fs->file_close(fh);
    (void)std::remove(path.c_str());
    return true;
}

static bool gfx_backend_supported(const std::string& name) {
    if (name.empty()) {
        return true; /* auto */
    }
    if (name == "soft") return true;
    if (name == "dx9") return true;
    if (name == "dx11") return true;
    if (name == "gl2") return true;
    if (name == "vk1") return true;
    if (name == "metal") return true;
    if (name == "gdi") return true;
    if (name == "null") return true;
    return false;
}

static bool profile_allows_backend(const LauncherProfile* profile,
                                   const std::string& subsystem_key,
                                   const std::string& backend_name) {
    size_t i;
    bool has_rules = false;
    if (!profile) {
        return true;
    }
    for (i = 0u; i < profile->allowed_backends.size(); ++i) {
        if (profile->allowed_backends[i].subsystem_key == subsystem_key) {
            has_rules = true;
            break;
        }
    }
    if (!has_rules) {
        return true;
    }
    for (i = 0u; i < profile->allowed_backends.size(); ++i) {
        if (profile->allowed_backends[i].subsystem_key == subsystem_key &&
            profile->allowed_backends[i].backend_name == backend_name) {
            return true;
        }
    }
    return false;
}

static std::string profile_pick_backend(const LauncherProfile* profile,
                                        const std::string& subsystem_key,
                                        const std::string& preferred_a,
                                        const std::string& preferred_b) {
    size_t i;
    if (!profile) {
        return preferred_a;
    }

    if (!preferred_a.empty() && profile_allows_backend(profile, subsystem_key, preferred_a)) {
        return preferred_a;
    }
    if (!preferred_b.empty() && profile_allows_backend(profile, subsystem_key, preferred_b)) {
        return preferred_b;
    }

    /* If subsystem is constrained, return the first allowed entry deterministically. */
    for (i = 0u; i < profile->allowed_backends.size(); ++i) {
        if (profile->allowed_backends[i].subsystem_key == subsystem_key) {
            return profile->allowed_backends[i].backend_name;
        }
    }

    return preferred_a;
}

static bool load_known_good_manifest(const launcher_services_api_v1* services,
                                     const LauncherInstancePaths& paths,
                                     LauncherInstanceManifest& out_manifest,
                                     std::string& out_prev_dir) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::vector<unsigned char> bytes;
    LauncherInstanceKnownGoodPointer kg;
    LauncherInstanceManifest m;
    std::string kg_path;
    std::string snapshot_root;
    std::string snapshot_manifest_path;

    out_prev_dir.clear();
    if (!services || !fs) {
        return false;
    }

    kg_path = path_join(paths.instance_root, "known_good.tlv");
    if (!fs_read_all(fs, kg_path, bytes) || bytes.empty()) {
        return false;
    }
    if (!launcher_instance_known_good_from_tlv_bytes(&bytes[0], bytes.size(), kg)) {
        return false;
    }
    if (kg.previous_dir.empty()) {
        return false;
    }

    snapshot_root = path_join(paths.previous_root, kg.previous_dir);
    snapshot_manifest_path = path_join(snapshot_root, "manifest.tlv");
    bytes.clear();
    if (!fs_read_all(fs, snapshot_manifest_path, bytes) || bytes.empty()) {
        return false;
    }
    if (!launcher_instance_manifest_from_tlv_bytes(&bytes[0], bytes.size(), m)) {
        return false;
    }

    if (kg.manifest_hash64 != 0ull) {
        const u64 got_hash = launcher_instance_manifest_hash64(m);
        if (got_hash != kg.manifest_hash64) {
            return false;
        }
    }

    out_prev_dir = kg.previous_dir;
    out_manifest = m;
    return true;
}

static LauncherInstanceManifest apply_safe_mode_manifest_overrides(const LauncherInstanceManifest& base,
                                                                   u32 disable_packs,
                                                                   u32 disable_mods) {
    LauncherInstanceManifest m = base;
    size_t i;
    for (i = 0u; i < m.content_entries.size(); ++i) {
        const u32 t = m.content_entries[i].type;
        if (disable_mods && t == (u32)LAUNCHER_CONTENT_MOD) {
            m.content_entries[i].enabled = 0u;
        }
        if (disable_packs && t == (u32)LAUNCHER_CONTENT_PACK) {
            m.content_entries[i].enabled = 0u;
        }
    }
    return m;
}

static bool validate_artifact_presence(const launcher_fs_api_v1* fs,
                                      const std::string& state_root,
                                      const LauncherInstanceManifest& manifest,
                                      std::vector<LauncherPrelaunchValidationFailure>& out_failures) {
    size_t i;
    for (i = 0u; i < manifest.content_entries.size(); ++i) {
        const LauncherContentEntry& e = manifest.content_entries[i];
        std::string dir, meta_path, payload_path;
        if (!e.enabled) {
            continue;
        }
        if (e.hash_bytes.empty()) {
            if (e.type == (u32)LAUNCHER_CONTENT_ENGINE ||
                e.type == (u32)LAUNCHER_CONTENT_GAME ||
                e.type == (u32)LAUNCHER_CONTENT_RUNTIME) {
                LauncherPrelaunchValidationFailure f;
                f.code = "missing_artifact_hash";
                f.suggestion = "repair_or_rollback";
                f.detail = std::string("content_id=") + e.id;
                out_failures.push_back(f);
                return false;
            }
            continue;
        }
        if (!launcher_artifact_store_paths(state_root, e.hash_bytes, dir, meta_path, payload_path)) {
            LauncherPrelaunchValidationFailure f;
            f.code = "artifact_paths_failed";
            f.suggestion = "repair_or_rollback";
            f.detail = std::string("content_id=") + e.id;
            out_failures.push_back(f);
            return false;
        }
        if (!fs_file_exists(fs, payload_path)) {
            LauncherPrelaunchValidationFailure f;
            f.code = "missing_artifact_payload";
            f.suggestion = "repair_or_rollback";
            f.detail = std::string("content_id=") + e.id + ";path=" + payload_path;
            out_failures.push_back(f);
            return false;
        }
    }
    return true;
}

static bool validate_simulation_safety(const launcher_services_api_v1* services,
                                      const LauncherInstanceManifest& manifest,
                                      const std::string& state_root,
                                      std::vector<LauncherPrelaunchValidationFailure>& out_failures) {
    std::string err;
    if (!launcher_pack_validate_simulation_safety(services, manifest, state_root, &err)) {
        LauncherPrelaunchValidationFailure f;
        f.code = "sim_safety";
        f.suggestion = "safe_mode_or_rollback";
        f.detail = err;
        out_failures.push_back(f);
        return false;
    }
    return true;
}

} /* namespace */

LauncherLaunchOverrides::LauncherLaunchOverrides()
    : request_safe_mode(0u),
      safe_mode_allow_network(0u),
      has_gfx_backend(0u),
      gfx_backend(),
      has_renderer_api(0u),
      renderer_api(),
      has_window_mode(0u),
      window_mode(0u),
      has_window_width(0u),
      window_width(0u),
      has_window_height(0u),
      window_height(0u),
      has_window_dpi(0u),
      window_dpi(0u),
      has_window_monitor(0u),
      window_monitor(0u),
      has_audio_device_id(0u),
      audio_device_id(),
      has_input_backend(0u),
      input_backend(),
      has_allow_network(0u),
      allow_network(0u),
      has_debug_flags(0u),
      debug_flags(0u) {
}

LauncherResolvedLaunchConfig::LauncherResolvedLaunchConfig()
    : safe_mode(0u),
      used_known_good_manifest(0u),
      known_good_previous_dir(),
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
      disable_mods(0u),
      disable_packs(0u),
      domain_overrides() {
}

namespace {

enum LauncherResolvedLaunchConfigTlvTag {
    LAUNCHER_RESOLVED_CFG_TLV_TAG_SAFE_MODE = 2u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_USED_KNOWN_GOOD = 3u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_KNOWN_GOOD_PREV_DIR = 4u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_GFX_BACKEND = 10u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_RENDERER_API = 11u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_MODE = 12u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_WIDTH = 13u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_HEIGHT = 14u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_DPI = 15u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_MONITOR = 16u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_AUDIO_DEVICE_ID = 20u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_INPUT_BACKEND = 21u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_ALLOW_NETWORK = 22u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_DEBUG_FLAGS = 23u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_DISABLE_MODS = 30u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_DISABLE_PACKS = 31u,
    LAUNCHER_RESOLVED_CFG_TLV_TAG_DOMAIN_OVERRIDE = 40u
};

static void encode_domain_override(TlvWriter& w, const LauncherDomainOverride& d) {
    TlvWriter inner;
    inner.add_string(LAUNCHER_INSTANCE_CONFIG_DOMAIN_TLV_TAG_DOMAIN_KEY, d.domain_key);
    inner.add_u32(LAUNCHER_INSTANCE_CONFIG_DOMAIN_TLV_TAG_ENABLED, d.enabled ? 1u : 0u);
    w.add_container(LAUNCHER_RESOLVED_CFG_TLV_TAG_DOMAIN_OVERRIDE, inner.bytes());
}

} /* namespace */

bool launcher_resolved_launch_config_to_tlv_bytes(const LauncherResolvedLaunchConfig& cfg,
                                                  std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_RESOLVED_LAUNCH_CONFIG_TLV_VERSION);
    w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_SAFE_MODE, cfg.safe_mode ? 1u : 0u);
    w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_USED_KNOWN_GOOD, cfg.used_known_good_manifest ? 1u : 0u);
    if (!cfg.known_good_previous_dir.empty()) {
        w.add_string(LAUNCHER_RESOLVED_CFG_TLV_TAG_KNOWN_GOOD_PREV_DIR, cfg.known_good_previous_dir);
    }
    if (!cfg.gfx_backend.empty()) {
        w.add_string(LAUNCHER_RESOLVED_CFG_TLV_TAG_GFX_BACKEND, cfg.gfx_backend);
    }
    if (!cfg.renderer_api.empty()) {
        w.add_string(LAUNCHER_RESOLVED_CFG_TLV_TAG_RENDERER_API, cfg.renderer_api);
    }
    if (cfg.window_mode != LAUNCHER_WINDOW_MODE_AUTO) {
        w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_MODE, cfg.window_mode);
    }
    if (cfg.window_width != 0u) {
        w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_WIDTH, cfg.window_width);
    }
    if (cfg.window_height != 0u) {
        w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_HEIGHT, cfg.window_height);
    }
    if (cfg.window_dpi != 0u) {
        w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_DPI, cfg.window_dpi);
    }
    if (cfg.window_monitor != 0u) {
        w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_WINDOW_MONITOR, cfg.window_monitor);
    }
    if (!cfg.audio_device_id.empty()) {
        w.add_string(LAUNCHER_RESOLVED_CFG_TLV_TAG_AUDIO_DEVICE_ID, cfg.audio_device_id);
    }
    if (!cfg.input_backend.empty()) {
        w.add_string(LAUNCHER_RESOLVED_CFG_TLV_TAG_INPUT_BACKEND, cfg.input_backend);
    }
    w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_ALLOW_NETWORK, cfg.allow_network ? 1u : 0u);
    if (cfg.debug_flags != 0u) {
        w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_DEBUG_FLAGS, cfg.debug_flags);
    }
    if (cfg.disable_mods) {
        w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_DISABLE_MODS, 1u);
    }
    if (cfg.disable_packs) {
        w.add_u32(LAUNCHER_RESOLVED_CFG_TLV_TAG_DISABLE_PACKS, 1u);
    }
    for (i = 0u; i < cfg.domain_overrides.size(); ++i) {
        if (!cfg.domain_overrides[i].domain_key.empty()) {
            encode_domain_override(w, cfg.domain_overrides[i]);
        }
    }

    out_bytes = w.bytes();
    return true;
}

u64 launcher_resolved_launch_config_hash64(const LauncherResolvedLaunchConfig& cfg) {
    std::vector<unsigned char> bytes;
    if (!launcher_resolved_launch_config_to_tlv_bytes(cfg, bytes)) {
        return 0ull;
    }
    return tlv_fnv1a64(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size());
}

LauncherPrelaunchValidationFailure::LauncherPrelaunchValidationFailure()
    : code(), suggestion(), detail() {
}

LauncherPrelaunchValidationResult::LauncherPrelaunchValidationResult()
    : ok(0u), failures() {
}

LauncherPrelaunchPlan::LauncherPrelaunchPlan()
    : state_root(),
      instance_id(),
      persisted_config(),
      overrides(),
      resolved(),
      base_manifest(),
      effective_manifest(),
      base_manifest_hash64(0ull),
      resolved_config_hash64(0ull),
      validation() {
}

bool launcher_prelaunch_build_plan(const launcher_services_api_v1* services,
                                   const LauncherProfile* profile_constraints,
                                   const std::string& instance_id,
                                   const std::string& state_root_override,
                                   const LauncherLaunchOverrides& overrides,
                                   LauncherPrelaunchPlan& out_plan,
                                   LauncherAuditLog* audit,
                                   std::string* out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root = state_root_override;
    LauncherInstancePaths paths;
    LauncherInstanceManifest live;
    LauncherInstanceManifest base;
    LauncherInstanceManifest effective;
    LauncherInstanceConfig persisted;
    LauncherResolvedLaunchConfig resolved;
    LauncherPrelaunchValidationResult validation;
    std::vector<LauncherPrelaunchValidationFailure> failures;
    bool used_known_good = false;
    std::string prev_dir;

    if (out_error) {
        out_error->clear();
    }
    out_plan = LauncherPrelaunchPlan();

    if (!services || !fs) {
        if (out_error) *out_error = "missing_services_or_fs";
        return false;
    }
    if (instance_id.empty()) {
        if (out_error) *out_error = "empty_instance_id";
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        if (out_error) *out_error = "unsafe_instance_id";
        audit_reason(audit, std::string("prelaunch;result=fail;code=unsafe_instance_id;instance_id=") + instance_id);
        return false;
    }
    if (state_root.empty()) {
        if (!get_state_root(fs, state_root)) {
            if (out_error) *out_error = "missing_state_root";
            return false;
        }
    }
    paths = launcher_instance_paths_make(state_root, instance_id);

    if (!launcher_instance_load_manifest(services, instance_id, state_root, live)) {
        if (out_error) *out_error = "load_manifest_failed";
        audit_reason(audit, std::string("prelaunch;result=fail;code=load_manifest;instance_id=") + instance_id);
        return false;
    }

    if (!launcher_instance_config_load(services, paths, persisted)) {
        if (out_error) *out_error = "load_config_failed";
        audit_reason(audit, std::string("prelaunch;result=fail;code=load_config;instance_id=") + instance_id);
        return false;
    }
    if (persisted.instance_id.empty()) {
        persisted.instance_id = instance_id;
    }

    base = live;
    if (overrides.request_safe_mode) {
        if (load_known_good_manifest(services, paths, base, prev_dir)) {
            used_known_good = true;
        } else {
            used_known_good = false;
        }
    }

    resolved.safe_mode = overrides.request_safe_mode ? 1u : 0u;
    resolved.used_known_good_manifest = used_known_good ? 1u : 0u;
    resolved.known_good_previous_dir = used_known_good ? prev_dir : std::string();

    /* Start from persisted defaults. */
    resolved.gfx_backend = persisted.gfx_backend;
    resolved.renderer_api = persisted.renderer_api;
    resolved.window_mode = persisted.window_mode;
    resolved.window_width = persisted.window_width;
    resolved.window_height = persisted.window_height;
    resolved.window_dpi = persisted.window_dpi;
    resolved.window_monitor = persisted.window_monitor;
    resolved.audio_device_id = persisted.audio_device_id;
    resolved.input_backend = persisted.input_backend;
    resolved.allow_network = persisted.allow_network ? 1u : 0u;
    resolved.debug_flags = persisted.debug_flags;
    resolved.domain_overrides = persisted.domain_overrides;

    /* Apply user overrides. */
    if (overrides.has_gfx_backend) {
        resolved.gfx_backend = overrides.gfx_backend;
    }
    if (overrides.has_renderer_api) {
        resolved.renderer_api = overrides.renderer_api;
    }
    if (overrides.has_window_mode) {
        resolved.window_mode = overrides.window_mode;
    }
    if (overrides.has_window_width) {
        resolved.window_width = overrides.window_width;
    }
    if (overrides.has_window_height) {
        resolved.window_height = overrides.window_height;
    }
    if (overrides.has_window_dpi) {
        resolved.window_dpi = overrides.window_dpi;
    }
    if (overrides.has_window_monitor) {
        resolved.window_monitor = overrides.window_monitor;
    }
    if (overrides.has_audio_device_id) {
        resolved.audio_device_id = overrides.audio_device_id;
    }
    if (overrides.has_input_backend) {
        resolved.input_backend = overrides.input_backend;
    }
    if (overrides.has_allow_network) {
        resolved.allow_network = overrides.allow_network ? 1u : 0u;
    }
    if (overrides.has_debug_flags) {
        resolved.debug_flags = overrides.debug_flags;
    }

    /* Safe-mode profile overlay (does not persist). */
    if (resolved.safe_mode) {
        resolved.disable_mods = 1u;
        resolved.disable_packs = 1u;
        resolved.allow_network = overrides.safe_mode_allow_network ? 1u : 0u;
        resolved.gfx_backend = "null";
    }

    /* Apply profile constraints deterministically. */
    resolved.gfx_backend = profile_pick_backend(profile_constraints,
                                               "gfx",
                                               resolved.gfx_backend,
                                               resolved.safe_mode ? std::string("soft") : std::string());
    if (!profile_allows_backend(profile_constraints, "gfx", resolved.gfx_backend) && !resolved.gfx_backend.empty()) {
        resolved.gfx_backend.clear();
    }

    effective = resolved.safe_mode ? apply_safe_mode_manifest_overrides(base, resolved.disable_packs, resolved.disable_mods) : base;

    /* Validation: renderer/backend compatibility */
    if (!gfx_backend_supported(resolved.gfx_backend)) {
        LauncherPrelaunchValidationFailure f;
        f.code = "gfx_backend_unsupported";
        f.suggestion = resolved.safe_mode ? "use_null_or_soft" : "choose_supported_backend";
        f.detail = resolved.gfx_backend;
        failures.push_back(f);
    }

    /* Validation: required artifacts present */
    (void)validate_artifact_presence(fs, state_root, effective, failures);

    /* Validation: simulation safety (pack ecosystem) */
    (void)validate_simulation_safety(services, effective, state_root, failures);

    /* Validation: writable logs directory (minimal probe) */
    if (!fs_write_probe(fs, path_join(paths.logs_root, "prelaunch_writable_probe.tmp"))) {
        LauncherPrelaunchValidationFailure f;
        f.code = "logs_not_writable";
        f.suggestion = "fix_permissions";
        f.detail = paths.logs_root;
        failures.push_back(f);
    }

    validation.ok = failures.empty() ? 1u : 0u;
    validation.failures = failures;

    if (!validation.ok) {
        audit_reason(audit, std::string("prelaunch;result=refuse;instance_id=") + instance_id);
    } else {
        audit_reason(audit, std::string("prelaunch;result=ok;instance_id=") + instance_id);
    }

    out_plan.state_root = state_root;
    out_plan.instance_id = instance_id;
    out_plan.persisted_config = persisted;
    out_plan.overrides = overrides;
    out_plan.resolved = resolved;
    out_plan.base_manifest = base;
    out_plan.effective_manifest = effective;
    out_plan.base_manifest_hash64 = launcher_instance_manifest_hash64(base);
    out_plan.resolved_config_hash64 = launcher_resolved_launch_config_hash64(resolved);
    out_plan.validation = validation;

    if (!out_plan.validation.ok) {
        if (out_error) {
            *out_error = validation.failures.empty() ? "validation_failed" : std::string("validation_failed:") + validation.failures[0].code;
        }
        return true;
    }

    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
