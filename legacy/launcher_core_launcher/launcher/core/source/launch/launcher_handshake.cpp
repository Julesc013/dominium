/*
FILE: source/dominium/launcher/core/src/launch/launcher_handshake.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / handshake
RESPONSIBILITY: Implements launcher handshake TLV encode/decode and deterministic validation helpers.
*/

#include "launcher_handshake.h"

#include <algorithm>
#include <cstring>

#include "launcher_pack_resolver.h"
#include "launcher_log.h"
#include "launcher_safety.h"
#include "launcher_sha256.h"
#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

static bool str_lt(const std::string& a, const std::string& b) {
    return a < b;
}

static void sort_strings(std::vector<std::string>& v) {
    std::sort(v.begin(), v.end(), str_lt);
}

static bool bytes_eq(const std::vector<unsigned char>& a, const std::vector<unsigned char>& b) {
    if (a.size() != b.size()) return false;
    if (a.empty()) return true;
    return std::memcmp(&a[0], &b[0], a.size()) == 0;
}

static bool bytes_empty_or_eq(const std::vector<unsigned char>& a, const std::vector<unsigned char>& b) {
    if (a.empty() && b.empty()) return true;
    return bytes_eq(a, b);
}

static bool string_vec_eq_sorted(std::vector<std::string> a, std::vector<std::string> b) {
    sort_strings(a);
    sort_strings(b);
    return a == b;
}

static bool has_required_fields(const LauncherHandshake& hs) {
    if (hs.schema_version != LAUNCHER_HANDSHAKE_TLV_VERSION) return false;
    if (hs.run_id == 0ull) return false;
    if (hs.instance_id.empty()) return false;
    if (hs.instance_manifest_hash_bytes.empty()) return false;
    if (hs.launcher_profile_id.empty()) return false;
    if (hs.determinism_profile_id.empty()) return false;
    if (hs.selected_platform_backends.empty()) return false;
    if (hs.selected_ui_backend_id.empty()) return false;
    if (hs.pinned_engine_build_id.empty()) return false;
    if (hs.pinned_game_build_id.empty()) return false;
    if (!hs.has_sim_caps) return false;
    if (!hs.has_feature_epoch) return false;
    if (!hs.has_coredata_sim_hash) return false;
    if (hs.timestamp_monotonic_us == 0ull) return false;
    return true;
}

static void stable_sort_pack_flags(LauncherHandshakePackEntry& e) {
    sort_strings(e.sim_affecting_flags);
    sort_strings(e.safe_mode_flags);
}

enum {
    HANDSHAKE_IDENTITY_TLV_VERSION = 2u,
    HANDSHAKE_IDENTITY_TLV_TAG_SIM_CAPS_HASH = 2u,
    HANDSHAKE_IDENTITY_TLV_TAG_PROVIDER_BINDINGS_HASH = 3u,
    HANDSHAKE_IDENTITY_TLV_TAG_PACK_ENTRY = 4u,
    HANDSHAKE_IDENTITY_TLV_TAG_FEATURE_EPOCH = 5u,
    HANDSHAKE_IDENTITY_TLV_TAG_COREDATA_SIM_HASH = 6u
};

enum {
    HANDSHAKE_IDENTITY_PACK_TLV_TAG_PACK_ID = 1u,
    HANDSHAKE_IDENTITY_PACK_TLV_TAG_VERSION = 2u,
    HANDSHAKE_IDENTITY_PACK_TLV_TAG_HASH_BYTES = 3u,
    HANDSHAKE_IDENTITY_PACK_TLV_TAG_SIM_FLAG = 4u
};

static bool build_identity_tlv(const LauncherHandshake& hs, std::vector<unsigned char>& out) {
    TlvWriter w;
    DomSimCaps sim_caps = hs.sim_caps;
    std::vector<unsigned char> sim_caps_bytes;
    const u64 provider_hash = hs.has_provider_bindings_hash ? hs.provider_bindings_hash64 : 0ull;
    u64 sim_caps_hash = 0ull;
    size_t i;

    if (!hs.has_sim_caps) {
        dom_sim_caps_init_default(sim_caps);
    }
    if (!dom_sim_caps_to_tlv(sim_caps, sim_caps_bytes)) {
        return false;
    }
    sim_caps_hash = tlv_fnv1a64(sim_caps_bytes.empty() ? (const unsigned char*)0 : &sim_caps_bytes[0],
                                sim_caps_bytes.size());

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, HANDSHAKE_IDENTITY_TLV_VERSION);
    w.add_u64(HANDSHAKE_IDENTITY_TLV_TAG_SIM_CAPS_HASH, sim_caps_hash);
    w.add_u64(HANDSHAKE_IDENTITY_TLV_TAG_PROVIDER_BINDINGS_HASH, provider_hash);
    w.add_u32(HANDSHAKE_IDENTITY_TLV_TAG_FEATURE_EPOCH,
              hs.has_feature_epoch ? hs.feature_epoch : 0u);
    w.add_u64(HANDSHAKE_IDENTITY_TLV_TAG_COREDATA_SIM_HASH,
              hs.has_coredata_sim_hash ? hs.coredata_sim_hash64 : 0ull);

    for (i = 0u; i < hs.resolved_packs.size(); ++i) {
        LauncherHandshakePackEntry e = hs.resolved_packs[i];
        TlvWriter ew;
        size_t j;

        if (!e.enabled) {
            continue;
        }

        stable_sort_pack_flags(e);
        ew.add_string(HANDSHAKE_IDENTITY_PACK_TLV_TAG_PACK_ID, e.pack_id);
        ew.add_string(HANDSHAKE_IDENTITY_PACK_TLV_TAG_VERSION, e.version);
        if (!e.hash_bytes.empty()) {
            ew.add_bytes(HANDSHAKE_IDENTITY_PACK_TLV_TAG_HASH_BYTES,
                         &e.hash_bytes[0],
                         (u32)e.hash_bytes.size());
        } else {
            ew.add_bytes(HANDSHAKE_IDENTITY_PACK_TLV_TAG_HASH_BYTES,
                         (const unsigned char*)0,
                         0u);
        }
        for (j = 0u; j < e.sim_affecting_flags.size(); ++j) {
            ew.add_string(HANDSHAKE_IDENTITY_PACK_TLV_TAG_SIM_FLAG, e.sim_affecting_flags[j]);
        }
        w.add_container(HANDSHAKE_IDENTITY_TLV_TAG_PACK_ENTRY, ew.bytes());
    }

    out = w.bytes();
    return true;
}

static std::vector<unsigned char> sha256_of_manifest(const LauncherInstanceManifest& m) {
    std::vector<unsigned char> tlv;
    unsigned char h[LAUNCHER_SHA256_BYTES];
    std::vector<unsigned char> out;
    std::memset(h, 0, sizeof(h));
    if (!launcher_instance_manifest_to_tlv_bytes(m, tlv)) {
        return out;
    }
    launcher_sha256_bytes(tlv.empty() ? (const unsigned char*)0 : &tlv[0], tlv.size(), h);
    out.assign(h, h + (size_t)LAUNCHER_SHA256_BYTES);
    return out;
}

static bool find_expected_pack(const std::vector<LauncherResolvedPack>& expected,
                               const std::string& pack_id,
                               LauncherResolvedPack& out) {
    size_t i;
    for (i = 0u; i < expected.size(); ++i) {
        if (expected[i].pack_id == pack_id) {
            out = expected[i];
            return true;
        }
    }
    return false;
}

static void emit_handshake_event(const launcher_services_api_v1* services,
                                 const LauncherHandshake& hs,
                                 const std::string& state_root_override,
                                 u32 event_code,
                                 u32 refusal_code,
                                 const err_t* err) {
    core_log_event ev;
    core_log_scope scope;
    const bool safe_id = (!hs.instance_id.empty() && launcher_is_safe_id_component(hs.instance_id));

    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_LAUNCHER;
    ev.code = (u16)event_code;
    ev.severity = (u8)((event_code == CORE_LOG_EVT_OP_FAIL) ? CORE_LOG_SEV_ERROR : CORE_LOG_SEV_INFO);
    ev.msg_id = 0u;
    ev.t_mono = 0u;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_OPERATION_ID, CORE_LOG_OP_LAUNCHER_HANDSHAKE_VALIDATE);
    if (hs.run_id != 0ull) {
        (void)core_log_event_add_u64(&ev, CORE_LOG_KEY_RUN_ID, hs.run_id);
    }
    if (refusal_code != 0u) {
        (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_REFUSAL_CODE, refusal_code);
    }
    if (err && !err_is_ok(err)) {
        launcher_log_add_err_fields(&ev, err);
    }

    std::memset(&scope, 0, sizeof(scope));
    scope.state_root = state_root_override.empty() ? (const char*)0 : state_root_override.c_str();
    if (safe_id && hs.run_id != 0ull) {
        scope.kind = CORE_LOG_SCOPE_RUN;
        scope.instance_id = hs.instance_id.c_str();
        scope.run_id = hs.run_id;
    } else if (safe_id) {
        scope.kind = CORE_LOG_SCOPE_INSTANCE;
        scope.instance_id = hs.instance_id.c_str();
    } else {
        scope.kind = CORE_LOG_SCOPE_GLOBAL;
    }
    (void)launcher_services_emit_event(services, &scope, &ev);
}

} /* namespace */

LauncherHandshakePackEntry::LauncherHandshakePackEntry()
    : pack_id(),
      version(),
      hash_bytes(),
      enabled(0u),
      sim_affecting_flags(),
      safe_mode_flags(),
      offline_mode_flag(0u) {
}

LauncherHandshake::LauncherHandshake()
    : schema_version(LAUNCHER_HANDSHAKE_TLV_VERSION),
      run_id(0ull),
      instance_id(),
      instance_manifest_hash_bytes(),
      launcher_profile_id(),
      determinism_profile_id(),
      selected_platform_backends(),
      selected_renderer_backends(),
      selected_ui_backend_id(),
      pinned_engine_build_id(),
      pinned_game_build_id(),
      resolved_packs(),
      sim_caps(),
      has_sim_caps(0u),
      perf_caps(),
      has_perf_caps(0u),
      has_provider_bindings_hash(0u),
      provider_bindings_hash64(0ull),
      has_feature_epoch(0u),
      feature_epoch(0u),
      has_coredata_sim_hash(0u),
      coredata_sim_hash64(0ull),
      timestamp_monotonic_us(0ull),
      has_timestamp_wall_us(0u),
      timestamp_wall_us(0ull) {
}

bool launcher_handshake_to_tlv_bytes(const LauncherHandshake& hs,
                                     std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;
    std::vector<std::string> platform = hs.selected_platform_backends;
    std::vector<std::string> renderer = hs.selected_renderer_backends;

    out_bytes.clear();

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_HANDSHAKE_TLV_VERSION);
    w.add_u64(LAUNCHER_HANDSHAKE_TLV_TAG_RUN_ID, hs.run_id);
    w.add_string(LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_ID, hs.instance_id);
    if (!hs.instance_manifest_hash_bytes.empty()) {
        w.add_bytes(LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH,
                    &hs.instance_manifest_hash_bytes[0],
                    (u32)hs.instance_manifest_hash_bytes.size());
    } else {
        w.add_bytes(LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH, (const unsigned char*)0, 0u);
    }
    w.add_string(LAUNCHER_HANDSHAKE_TLV_TAG_LAUNCHER_PROFILE_ID, hs.launcher_profile_id);
    w.add_string(LAUNCHER_HANDSHAKE_TLV_TAG_DETERMINISM_PROFILE_ID, hs.determinism_profile_id);

    sort_strings(platform);
    sort_strings(renderer);
    for (i = 0u; i < platform.size(); ++i) {
        w.add_string(LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_PLATFORM_BACKEND, platform[i]);
    }
    for (i = 0u; i < renderer.size(); ++i) {
        w.add_string(LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_RENDERER_BACKEND, renderer[i]);
    }

    w.add_string(LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_UI_BACKEND_ID, hs.selected_ui_backend_id);
    w.add_string(LAUNCHER_HANDSHAKE_TLV_TAG_PIN_ENGINE_BUILD_ID, hs.pinned_engine_build_id);
    w.add_string(LAUNCHER_HANDSHAKE_TLV_TAG_PIN_GAME_BUILD_ID, hs.pinned_game_build_id);

    for (i = 0u; i < hs.resolved_packs.size(); ++i) {
        LauncherHandshakePackEntry e = hs.resolved_packs[i];
        TlvWriter ew;
        size_t j;
        stable_sort_pack_flags(e);

        ew.add_string(LAUNCHER_HANDSHAKE_PACK_TLV_TAG_PACK_ID, e.pack_id);
        ew.add_string(LAUNCHER_HANDSHAKE_PACK_TLV_TAG_VERSION, e.version);
        if (!e.hash_bytes.empty()) {
            ew.add_bytes(LAUNCHER_HANDSHAKE_PACK_TLV_TAG_HASH_BYTES, &e.hash_bytes[0], (u32)e.hash_bytes.size());
        } else {
            ew.add_bytes(LAUNCHER_HANDSHAKE_PACK_TLV_TAG_HASH_BYTES, (const unsigned char*)0, 0u);
        }
        ew.add_u32(LAUNCHER_HANDSHAKE_PACK_TLV_TAG_ENABLED, e.enabled ? 1u : 0u);
        for (j = 0u; j < e.sim_affecting_flags.size(); ++j) {
            ew.add_string(LAUNCHER_HANDSHAKE_PACK_TLV_TAG_SIM_FLAG, e.sim_affecting_flags[j]);
        }
        for (j = 0u; j < e.safe_mode_flags.size(); ++j) {
            ew.add_string(LAUNCHER_HANDSHAKE_PACK_TLV_TAG_SAFE_MODE_FLAG, e.safe_mode_flags[j]);
        }
        ew.add_u32(LAUNCHER_HANDSHAKE_PACK_TLV_TAG_OFFLINE_MODE_FLAG, e.offline_mode_flag ? 1u : 0u);

        w.add_container(LAUNCHER_HANDSHAKE_TLV_TAG_RESOLVED_PACK_ENTRY, ew.bytes());
    }

    w.add_u64(LAUNCHER_HANDSHAKE_TLV_TAG_TIMESTAMP_MONOTONIC_US, hs.timestamp_monotonic_us);
    if (hs.has_timestamp_wall_us) {
        w.add_u64(LAUNCHER_HANDSHAKE_TLV_TAG_TIMESTAMP_WALL_US, hs.timestamp_wall_us);
    }
    if (hs.has_sim_caps) {
        std::vector<unsigned char> sim_bytes;
        if (dom_sim_caps_to_tlv(hs.sim_caps, sim_bytes)) {
            w.add_container(LAUNCHER_HANDSHAKE_TLV_TAG_SIM_CAPS, sim_bytes);
        }
    }
    if (hs.has_perf_caps) {
        std::vector<unsigned char> perf_bytes;
        if (dom_perf_caps_to_tlv(hs.perf_caps, perf_bytes)) {
            w.add_container(LAUNCHER_HANDSHAKE_TLV_TAG_PERF_CAPS, perf_bytes);
        }
    }
    if (hs.has_provider_bindings_hash) {
        w.add_u64(LAUNCHER_HANDSHAKE_TLV_TAG_PROVIDER_BINDINGS_HASH, hs.provider_bindings_hash64);
    }
    if (hs.has_feature_epoch) {
        w.add_u32(LAUNCHER_HANDSHAKE_TLV_TAG_FEATURE_EPOCH, hs.feature_epoch);
    }
    if (hs.has_coredata_sim_hash) {
        w.add_u64(LAUNCHER_HANDSHAKE_TLV_TAG_COREDATA_SIM_HASH, hs.coredata_sim_hash64);
    }

    out_bytes = w.bytes();
    return true;
}

bool launcher_handshake_from_tlv_bytes(const unsigned char* data,
                                       size_t size,
                                       LauncherHandshake& out_hs) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;

    out_hs = LauncherHandshake();
    if (!tlv_read_schema_version_or_default(data, size, version, LAUNCHER_HANDSHAKE_TLV_VERSION)) {
        return false;
    }
    if (version != LAUNCHER_HANDSHAKE_TLV_VERSION) {
        return false;
    }
    out_hs.schema_version = version;

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_RUN_ID: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_hs.run_id = v;
            }
            break;
        }
        case LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_ID:
            out_hs.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH:
            out_hs.instance_manifest_hash_bytes.assign(rec.payload, rec.payload + rec.len);
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_LAUNCHER_PROFILE_ID:
            out_hs.launcher_profile_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_DETERMINISM_PROFILE_ID:
            out_hs.determinism_profile_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_PLATFORM_BACKEND:
            out_hs.selected_platform_backends.push_back(tlv_read_string(rec.payload, rec.len));
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_RENDERER_BACKEND:
            out_hs.selected_renderer_backends.push_back(tlv_read_string(rec.payload, rec.len));
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_UI_BACKEND_ID:
            out_hs.selected_ui_backend_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_PIN_ENGINE_BUILD_ID:
            out_hs.pinned_engine_build_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_PIN_GAME_BUILD_ID:
            out_hs.pinned_game_build_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_HANDSHAKE_TLV_TAG_TIMESTAMP_MONOTONIC_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_hs.timestamp_monotonic_us = v;
            }
            break;
        }
        case LAUNCHER_HANDSHAKE_TLV_TAG_TIMESTAMP_WALL_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_hs.has_timestamp_wall_us = 1u;
                out_hs.timestamp_wall_us = v;
            }
            break;
        }
        case LAUNCHER_HANDSHAKE_TLV_TAG_SIM_CAPS: {
            DomSimCaps caps;
            if (dom_sim_caps_from_tlv(rec.payload, (u32)rec.len, caps)) {
                out_hs.sim_caps = caps;
                out_hs.has_sim_caps = 1u;
            }
            break;
        }
        case LAUNCHER_HANDSHAKE_TLV_TAG_PERF_CAPS: {
            DomPerfCaps caps;
            if (dom_perf_caps_from_tlv(rec.payload, (u32)rec.len, caps)) {
                out_hs.perf_caps = caps;
                out_hs.has_perf_caps = 1u;
            }
            break;
        }
        case LAUNCHER_HANDSHAKE_TLV_TAG_PROVIDER_BINDINGS_HASH: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_hs.has_provider_bindings_hash = 1u;
                out_hs.provider_bindings_hash64 = v;
            }
            break;
        }
        case LAUNCHER_HANDSHAKE_TLV_TAG_FEATURE_EPOCH: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                out_hs.has_feature_epoch = 1u;
                out_hs.feature_epoch = v;
            }
            break;
        }
        case LAUNCHER_HANDSHAKE_TLV_TAG_COREDATA_SIM_HASH: {
            u64 v = 0ull;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_hs.has_coredata_sim_hash = 1u;
                out_hs.coredata_sim_hash64 = v;
            }
            break;
        }
        case LAUNCHER_HANDSHAKE_TLV_TAG_RESOLVED_PACK_ENTRY: {
            LauncherHandshakePackEntry e;
            TlvReader er(rec.payload, (size_t)rec.len);
            TlvRecord pr;
            while (er.next(pr)) {
                switch (pr.tag) {
                case LAUNCHER_HANDSHAKE_PACK_TLV_TAG_PACK_ID:
                    e.pack_id = tlv_read_string(pr.payload, pr.len);
                    break;
                case LAUNCHER_HANDSHAKE_PACK_TLV_TAG_VERSION:
                    e.version = tlv_read_string(pr.payload, pr.len);
                    break;
                case LAUNCHER_HANDSHAKE_PACK_TLV_TAG_HASH_BYTES:
                    e.hash_bytes.assign(pr.payload, pr.payload + pr.len);
                    break;
                case LAUNCHER_HANDSHAKE_PACK_TLV_TAG_ENABLED: {
                    u32 v;
                    if (tlv_read_u32_le(pr.payload, pr.len, v)) {
                        e.enabled = (v != 0u) ? 1u : 0u;
                    }
                    break;
                }
                case LAUNCHER_HANDSHAKE_PACK_TLV_TAG_SIM_FLAG:
                    e.sim_affecting_flags.push_back(tlv_read_string(pr.payload, pr.len));
                    break;
                case LAUNCHER_HANDSHAKE_PACK_TLV_TAG_SAFE_MODE_FLAG:
                    e.safe_mode_flags.push_back(tlv_read_string(pr.payload, pr.len));
                    break;
                case LAUNCHER_HANDSHAKE_PACK_TLV_TAG_OFFLINE_MODE_FLAG: {
                    u32 v;
                    if (tlv_read_u32_le(pr.payload, pr.len, v)) {
                        e.offline_mode_flag = (v != 0u) ? 1u : 0u;
                    }
                    break;
                }
                default:
                    /* skip unknown */
                    break;
                }
            }
            out_hs.resolved_packs.push_back(e);
            break;
        }
        default:
            /* skip unknown */
            break;
        }
    }

    return true;
}

u64 launcher_handshake_hash64(const LauncherHandshake& hs) {
    std::vector<unsigned char> bytes;
    if (!build_identity_tlv(hs, bytes)) {
        return 0ull;
    }
    return tlv_fnv1a64(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size());
}

static err_t handshake_err_from_refusal(u32 refusal) {
    switch (refusal) {
    case LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS:
        return err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_HANDSHAKE_INVALID,
                        (u32)(ERRF_POLICY_REFUSAL | ERRF_USER_ACTIONABLE), (u32)ERRMSG_LAUNCHER_HANDSHAKE_INVALID);
    case LAUNCHER_HANDSHAKE_REFUSAL_MANIFEST_HASH_MISMATCH:
        return err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_HANDSHAKE_INVALID,
                        (u32)ERRF_INTEGRITY, (u32)ERRMSG_LAUNCHER_HANDSHAKE_INVALID);
    case LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS:
        return err_make((u16)ERRD_PACKS, (u16)ERRC_PACKS_SIM_FLAGS_MISSING,
                        (u32)(ERRF_POLICY_REFUSAL | ERRF_USER_ACTIONABLE), (u32)ERRMSG_PACKS_SIM_FLAGS_MISSING);
    case LAUNCHER_HANDSHAKE_REFUSAL_PACK_HASH_MISMATCH:
        return err_make((u16)ERRD_ARTIFACT, (u16)ERRC_ARTIFACT_PAYLOAD_HASH_MISMATCH,
                        (u32)ERRF_INTEGRITY, (u32)ERRMSG_ARTIFACT_PAYLOAD_HASH_MISMATCH);
    case LAUNCHER_HANDSHAKE_REFUSAL_PRELAUNCH_VALIDATION_FAILED:
        return err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_HANDSHAKE_INVALID,
                        (u32)ERRF_POLICY_REFUSAL, (u32)ERRMSG_LAUNCHER_HANDSHAKE_INVALID);
    default:
        return err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_HANDSHAKE_INVALID,
                        (u32)ERRF_POLICY_REFUSAL, (u32)ERRMSG_LAUNCHER_HANDSHAKE_INVALID);
    }
}

u32 launcher_handshake_validate(const launcher_services_api_v1* services,
                                const LauncherHandshake& hs,
                                const LauncherInstanceManifest& manifest,
                                const std::string& state_root_override,
                                std::string* out_detail) {
    std::vector<unsigned char> expected_manifest_hash = sha256_of_manifest(manifest);
    std::vector<LauncherResolvedPack> expected_ordered;
    std::string err;
    size_t i;

    if (out_detail) {
        out_detail->clear();
    }

    if (!has_required_fields(hs)) {
        if (out_detail) {
            *out_detail = "missing_required_fields";
        }
        {
            const err_t err = handshake_err_from_refusal((u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS);
            emit_handshake_event(services, hs, state_root_override, CORE_LOG_EVT_OP_FAIL,
                                 (u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS, &err);
        }
        return (u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
    }
    if (!bytes_eq(hs.instance_manifest_hash_bytes, expected_manifest_hash)) {
        if (out_detail) {
            *out_detail = "instance_manifest_hash_mismatch";
        }
        {
            const err_t err = handshake_err_from_refusal((u32)LAUNCHER_HANDSHAKE_REFUSAL_MANIFEST_HASH_MISMATCH);
            emit_handshake_event(services, hs, state_root_override, CORE_LOG_EVT_OP_FAIL,
                                 (u32)LAUNCHER_HANDSHAKE_REFUSAL_MANIFEST_HASH_MISMATCH, &err);
        }
        return (u32)LAUNCHER_HANDSHAKE_REFUSAL_MANIFEST_HASH_MISMATCH;
    }

    if (!launcher_pack_resolve_enabled(services, manifest, state_root_override, expected_ordered, &err)) {
        if (out_detail) {
            *out_detail = std::string("pack_resolve_failed;") + err;
        }
        {
            const err_t e = handshake_err_from_refusal((u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS);
            emit_handshake_event(services, hs, state_root_override, CORE_LOG_EVT_OP_FAIL,
                                 (u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS, &e);
        }
        return (u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS;
    }

    for (i = 0u; i < expected_ordered.size(); ++i) {
        const LauncherResolvedPack& exp = expected_ordered[i];
        LauncherResolvedPack tmp;
        LauncherHandshakePackEntry got;
        bool found = false;
        size_t j;
        for (j = 0u; j < hs.resolved_packs.size(); ++j) {
            if (hs.resolved_packs[j].pack_id == exp.pack_id) {
                got = hs.resolved_packs[j];
                found = true;
                break;
            }
        }
        if (!found) {
            if (!exp.sim_affecting_flags.empty()) {
                if (out_detail) {
                    *out_detail = std::string("missing_sim_affecting_pack;pack_id=") + exp.pack_id;
                }
                {
                    const err_t e = handshake_err_from_refusal((u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS);
                    emit_handshake_event(services, hs, state_root_override, CORE_LOG_EVT_OP_FAIL,
                                         (u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS, &e);
                }
                return (u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS;
            }
            continue;
        }
        /* Pack hash mismatch */
            if (!bytes_empty_or_eq(got.hash_bytes, exp.artifact_hash_bytes) && got.enabled) {
                if (out_detail) {
                    *out_detail = std::string("pack_hash_mismatch;pack_id=") + exp.pack_id;
                }
                {
                    const err_t e = handshake_err_from_refusal((u32)LAUNCHER_HANDSHAKE_REFUSAL_PACK_HASH_MISMATCH);
                    emit_handshake_event(services, hs, state_root_override, CORE_LOG_EVT_OP_FAIL,
                                         (u32)LAUNCHER_HANDSHAKE_REFUSAL_PACK_HASH_MISMATCH, &e);
                }
                return (u32)LAUNCHER_HANDSHAKE_REFUSAL_PACK_HASH_MISMATCH;
            }
        /* Sim-affecting flags must be declared and match deterministically. */
        tmp = LauncherResolvedPack();
        if (find_expected_pack(expected_ordered, exp.pack_id, tmp) && !tmp.sim_affecting_flags.empty()) {
            if (!string_vec_eq_sorted(got.sim_affecting_flags, tmp.sim_affecting_flags)) {
                if (out_detail) {
                    *out_detail = std::string("sim_flags_mismatch;pack_id=") + exp.pack_id;
                }
                {
                    const err_t e = handshake_err_from_refusal((u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS);
                    emit_handshake_event(services, hs, state_root_override, CORE_LOG_EVT_OP_FAIL,
                                         (u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS, &e);
                }
                return (u32)LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS;
            }
        }
    }
    emit_handshake_event(services, hs, state_root_override, CORE_LOG_EVT_OP_OK, 0u, (const err_t*)0);
    return (u32)LAUNCHER_HANDSHAKE_REFUSAL_OK;
}

bool launcher_handshake_validate_ex(const launcher_services_api_v1* services,
                                    const LauncherHandshake& hs,
                                    const LauncherInstanceManifest& manifest,
                                    const std::string& state_root_override,
                                    err_t* out_err) {
    u32 refusal;
    std::string detail;
    refusal = launcher_handshake_validate(services, hs, manifest, state_root_override, &detail);
    if (refusal == (u32)LAUNCHER_HANDSHAKE_REFUSAL_OK) {
        if (out_err) {
            *out_err = err_ok();
        }
        return true;
    }
    if (out_err) {
        *out_err = handshake_err_from_refusal(refusal);
    }
    return false;
}

} /* namespace launcher_core */
} /* namespace dom */

