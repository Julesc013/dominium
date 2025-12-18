/*
FILE: source/dominium/launcher/core/include/launcher_instance_config.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_config
RESPONSIBILITY: Instance-scoped launcher configuration overrides (separate from manifest) + TLV persistence (versioned; skip-unknown; deterministic).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core TLV helpers and unknown-record model.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Serialization is canonical and order-preserving; unknown tags are skipped and preserved.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_CONFIG_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_CONFIG_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "launcher_core_api.h"
}

#include "launcher_instance.h" /* LauncherTlvUnknownRecord */
#include "launcher_instance_ops.h" /* LauncherInstancePaths */

namespace dom {
namespace launcher_core {

/* TLV schema version for config/config.tlv root. */
enum { LAUNCHER_INSTANCE_CONFIG_TLV_VERSION = 1u };

/* config.tlv root records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_INSTANCE_ID` (string)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_GFX_BACKEND` (string, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_RENDERER_API` (string, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_MODE` (u32, optional; `LauncherWindowMode`)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_WIDTH` (u32, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_HEIGHT` (u32, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_DPI` (u32, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_MONITOR` (u32, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_AUDIO_DEVICE_ID` (string, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_INPUT_BACKEND` (string, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_ALLOW_NETWORK` (u32, optional; 0/1)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_DEBUG_FLAGS` (u32, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_DOMAIN_OVERRIDE` (container, repeated)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_AUTO_RECOVERY_THRESHOLD` (u32, optional)
 * - `LAUNCHER_INSTANCE_CONFIG_TLV_TAG_LAUNCH_HISTORY_MAX_ENTRIES` (u32, optional)
 */
enum LauncherInstanceConfigTlvTag {
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_INSTANCE_ID = 2u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_GFX_BACKEND = 3u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_RENDERER_API = 4u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_MODE = 5u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_WIDTH = 6u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_HEIGHT = 7u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_DPI = 8u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_WINDOW_MONITOR = 9u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_AUDIO_DEVICE_ID = 10u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_INPUT_BACKEND = 11u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_ALLOW_NETWORK = 12u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_DEBUG_FLAGS = 13u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_DOMAIN_OVERRIDE = 20u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_AUTO_RECOVERY_THRESHOLD = 30u,
    LAUNCHER_INSTANCE_CONFIG_TLV_TAG_LAUNCH_HISTORY_MAX_ENTRIES = 31u
};

enum LauncherInstanceConfigDomainTlvTag {
    LAUNCHER_INSTANCE_CONFIG_DOMAIN_TLV_TAG_DOMAIN_KEY = 1u,
    LAUNCHER_INSTANCE_CONFIG_DOMAIN_TLV_TAG_ENABLED = 2u
};

enum LauncherWindowMode {
    LAUNCHER_WINDOW_MODE_AUTO = 0u,
    LAUNCHER_WINDOW_MODE_WINDOWED = 1u,
    LAUNCHER_WINDOW_MODE_FULLSCREEN = 2u,
    LAUNCHER_WINDOW_MODE_BORDERLESS = 3u
};

/* Debug flags carried in `LauncherInstanceConfig::debug_flags` and propagated to
 * `LauncherResolvedLaunchConfig::debug_flags`.
 *
 * These are intended for deterministic, testable knobs (no OS-dependent behavior).
 */
enum LauncherDebugFlagBits {
    /* Stub: treat the launch as "network required". When `allow_network=0`, prelaunch must refuse. */
    LAUNCHER_DEBUG_FLAG_STUB_NETWORK_REQUIRED = 0x00000001u
};

struct LauncherDomainOverride {
    std::string domain_key;
    u32 enabled; /* 0/1 */
    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherDomainOverride();
};

struct LauncherInstanceConfig {
    u32 schema_version;
    std::string instance_id;

    /* Overrides (when empty/0 => use defaults). */
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

    std::vector<LauncherDomainOverride> domain_overrides;

    /* Auto-recovery tuning. */
    u32 auto_recovery_failure_threshold;
    u32 launch_history_max_entries;

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherInstanceConfig();
};

LauncherInstanceConfig launcher_instance_config_make_default(const std::string& instance_id);

bool launcher_instance_config_to_tlv_bytes(const LauncherInstanceConfig& cfg,
                                           std::vector<unsigned char>& out_bytes);
bool launcher_instance_config_from_tlv_bytes(const unsigned char* data,
                                             size_t size,
                                             LauncherInstanceConfig& out_cfg);

/* File helpers:
 * - Path: `<instance_root>/config/config.tlv` (see `LauncherInstancePaths`).
 * - Missing file => returns defaults.
 */
bool launcher_instance_config_load(const launcher_services_api_v1* services,
                                   const LauncherInstancePaths& paths,
                                   LauncherInstanceConfig& out_cfg);
bool launcher_instance_config_store(const launcher_services_api_v1* services,
                                    const LauncherInstancePaths& paths,
                                    const LauncherInstanceConfig& cfg);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_CONFIG_H */
