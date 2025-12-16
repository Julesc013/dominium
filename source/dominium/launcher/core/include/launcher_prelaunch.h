/*
FILE: source/dominium/launcher/core/include/launcher_prelaunch.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / prelaunch
RESPONSIBILITY: Deterministic pre-launch configuration resolution, safe-mode selection, and validation (UI-agnostic; auditable).
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core instance/profile/pack/artifact models and services facade.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; detailed refusal reasons returned in out_error and recorded via audit when provided.
DETERMINISM: Resolution and validation are deterministic given explicit inputs and injected services; no filesystem enumeration ordering.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_PRELAUNCH_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_PRELAUNCH_H

#include <string>
#include <vector>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance.h"
#include "launcher_instance_config.h"
#include "launcher_profile.h"

namespace dom {
namespace launcher_core {

struct LauncherAuditLog; /* forward-declared; see launcher_audit.h */

struct LauncherLaunchOverrides {
    u32 request_safe_mode; /* 0/1 */
    u32 safe_mode_allow_network; /* 0/1; only used when request_safe_mode=1 */

    u32 has_gfx_backend;  /* 0/1 */
    std::string gfx_backend;

    u32 has_renderer_api; /* 0/1 */
    std::string renderer_api;

    u32 has_window_mode;  /* 0/1 */
    u32 window_mode;
    u32 has_window_width; /* 0/1 */
    u32 window_width;
    u32 has_window_height; /* 0/1 */
    u32 window_height;
    u32 has_window_dpi;    /* 0/1 */
    u32 window_dpi;
    u32 has_window_monitor; /* 0/1 */
    u32 window_monitor;

    u32 has_audio_device_id; /* 0/1 */
    std::string audio_device_id;
    u32 has_input_backend;   /* 0/1 */
    std::string input_backend;

    u32 has_allow_network; /* 0/1 */
    u32 allow_network;     /* 0/1 */

    u32 has_debug_flags; /* 0/1 */
    u32 debug_flags;

    LauncherLaunchOverrides();
};

struct LauncherResolvedLaunchConfig {
    u32 safe_mode; /* 0/1 */
    u32 used_known_good_manifest; /* 0/1 */
    std::string known_good_previous_dir; /* when used_known_good_manifest==1 */

    /* Effective knobs */
    std::string gfx_backend;
    std::string renderer_api;
    u32 window_mode;
    u32 window_width;
    u32 window_height;
    u32 window_dpi;
    u32 window_monitor;
    std::string audio_device_id;
    std::string input_backend;
    u32 allow_network; /* 0/1 */
    u32 debug_flags;

    /* Safe-mode derived behavior */
    u32 disable_mods;  /* 0/1 */
    u32 disable_packs; /* 0/1 */

    std::vector<LauncherDomainOverride> domain_overrides;

    LauncherResolvedLaunchConfig();
};

enum { LAUNCHER_RESOLVED_LAUNCH_CONFIG_TLV_VERSION = 1u };

bool launcher_resolved_launch_config_to_tlv_bytes(const LauncherResolvedLaunchConfig& cfg,
                                                  std::vector<unsigned char>& out_bytes);
u64 launcher_resolved_launch_config_hash64(const LauncherResolvedLaunchConfig& cfg);

struct LauncherPrelaunchValidationFailure {
    std::string code;
    std::string suggestion;
    std::string detail;

    LauncherPrelaunchValidationFailure();
};

struct LauncherPrelaunchValidationResult {
    u32 ok; /* 0/1 */
    std::vector<LauncherPrelaunchValidationFailure> failures;

    LauncherPrelaunchValidationResult();
};

struct LauncherPrelaunchPlan {
    std::string state_root;
    std::string instance_id;

    LauncherInstanceConfig persisted_config;
    LauncherLaunchOverrides overrides;
    LauncherResolvedLaunchConfig resolved;

    LauncherInstanceManifest base_manifest;      /* live or known-good snapshot */
    LauncherInstanceManifest effective_manifest; /* safe-mode disables applied */

    u64 base_manifest_hash64;
    u64 resolved_config_hash64;

    LauncherPrelaunchValidationResult validation;

    LauncherPrelaunchPlan();
};

/* Builds a deterministic launch plan (no process spawn):
 * - Loads live manifest + config/config.tlv
 * - Applies safe-mode manifest selection and override layering
 * - Applies safe-mode mod/pack disabling to produce an effective manifest copy
 * - Runs deterministic validation checks
 * - Computes a stable config hash for failure tracking/audit
 */
bool launcher_prelaunch_build_plan(const launcher_services_api_v1* services,
                                   const LauncherProfile* profile_constraints, /* optional; may be NULL */
                                   const std::string& instance_id,
                                   const std::string& state_root_override,
                                   const LauncherLaunchOverrides& overrides,
                                   LauncherPrelaunchPlan& out_plan,
                                   LauncherAuditLog* audit,
                                   std::string* out_error);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_PRELAUNCH_H */

