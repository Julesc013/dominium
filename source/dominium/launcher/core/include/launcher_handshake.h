/*
FILE: source/dominium/launcher/core/include/launcher_handshake.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / handshake
RESPONSIBILITY: Launcher↔engine handshake TLV schema + deterministic encode/decode + launcher-side validation helpers.
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core instance/pack models; services facade types only.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Canonical encoding with explicit ordering; integers are little-endian; skip-unknown supported.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_HANDSHAKE_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_HANDSHAKE_H

#include <string>
#include <vector>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance.h"

namespace dom {
namespace launcher_core {

/* TLV schema version for launcher_handshake.tlv root. */
enum { LAUNCHER_HANDSHAKE_TLV_VERSION = 1u };

/* launcher_handshake.tlv schema (versioned root; skip-unknown; canonical ordering).
 *
 * Root required fields:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_HANDSHAKE_TLV_VERSION`.
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_RUN_ID` (u64)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_ID` (string)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH` (bytes; SHA-256 recommended)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_LAUNCHER_PROFILE_ID` (string)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_DETERMINISM_PROFILE_ID` (string)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_PLATFORM_BACKEND` (string, repeated)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_RENDERER_BACKEND` (string, repeated; may be empty)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_UI_BACKEND_ID` (string)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_PIN_ENGINE_BUILD_ID` (string)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_PIN_GAME_BUILD_ID` (string)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_RESOLVED_PACK_ENTRY` (container, repeated; order preserved)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_TIMESTAMP_MONOTONIC_US` (u64)
 * - `LAUNCHER_HANDSHAKE_TLV_TAG_TIMESTAMP_WALL_US` (u64, optional)
 *
 * Resolved-pack entry payload (container TLV):
 * - `LAUNCHER_HANDSHAKE_PACK_TLV_TAG_PACK_ID` (string)
 * - `LAUNCHER_HANDSHAKE_PACK_TLV_TAG_VERSION` (string)
 * - `LAUNCHER_HANDSHAKE_PACK_TLV_TAG_HASH_BYTES` (bytes)
 * - `LAUNCHER_HANDSHAKE_PACK_TLV_TAG_ENABLED` (u32; 0/1)
 * - `LAUNCHER_HANDSHAKE_PACK_TLV_TAG_SIM_FLAG` (string, repeated)
 * - `LAUNCHER_HANDSHAKE_PACK_TLV_TAG_SAFE_MODE_FLAG` (string, repeated)
 * - `LAUNCHER_HANDSHAKE_PACK_TLV_TAG_OFFLINE_MODE_FLAG` (u32; 0/1)
 */
enum LauncherHandshakeTlvTag {
    LAUNCHER_HANDSHAKE_TLV_TAG_RUN_ID = 2u,
    LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_ID = 3u,
    LAUNCHER_HANDSHAKE_TLV_TAG_INSTANCE_MANIFEST_HASH = 4u,
    LAUNCHER_HANDSHAKE_TLV_TAG_LAUNCHER_PROFILE_ID = 5u,
    LAUNCHER_HANDSHAKE_TLV_TAG_DETERMINISM_PROFILE_ID = 6u,
    LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_PLATFORM_BACKEND = 7u,
    LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_RENDERER_BACKEND = 8u,
    LAUNCHER_HANDSHAKE_TLV_TAG_SELECTED_UI_BACKEND_ID = 9u,
    LAUNCHER_HANDSHAKE_TLV_TAG_PIN_ENGINE_BUILD_ID = 10u,
    LAUNCHER_HANDSHAKE_TLV_TAG_PIN_GAME_BUILD_ID = 11u,
    LAUNCHER_HANDSHAKE_TLV_TAG_RESOLVED_PACK_ENTRY = 12u,
    LAUNCHER_HANDSHAKE_TLV_TAG_TIMESTAMP_MONOTONIC_US = 13u,
    LAUNCHER_HANDSHAKE_TLV_TAG_TIMESTAMP_WALL_US = 14u
};

enum LauncherHandshakePackTlvTag {
    LAUNCHER_HANDSHAKE_PACK_TLV_TAG_PACK_ID = 1u,
    LAUNCHER_HANDSHAKE_PACK_TLV_TAG_VERSION = 2u,
    LAUNCHER_HANDSHAKE_PACK_TLV_TAG_HASH_BYTES = 3u,
    LAUNCHER_HANDSHAKE_PACK_TLV_TAG_ENABLED = 4u,
    LAUNCHER_HANDSHAKE_PACK_TLV_TAG_SIM_FLAG = 5u,
    LAUNCHER_HANDSHAKE_PACK_TLV_TAG_SAFE_MODE_FLAG = 6u,
    LAUNCHER_HANDSHAKE_PACK_TLV_TAG_OFFLINE_MODE_FLAG = 7u
};

struct LauncherHandshakePackEntry {
    std::string pack_id;
    std::string version;
    std::vector<unsigned char> hash_bytes;
    u32 enabled; /* 0/1 */

    std::vector<std::string> sim_affecting_flags;
    std::vector<std::string> safe_mode_flags;
    u32 offline_mode_flag; /* 0/1 */

    LauncherHandshakePackEntry();
};

struct LauncherHandshake {
    u32 schema_version;

    u64 run_id;
    std::string instance_id;
    std::vector<unsigned char> instance_manifest_hash_bytes;

    std::string launcher_profile_id;
    std::string determinism_profile_id;

    std::vector<std::string> selected_platform_backends;
    std::vector<std::string> selected_renderer_backends;
    std::string selected_ui_backend_id;

    std::string pinned_engine_build_id;
    std::string pinned_game_build_id;

    std::vector<LauncherHandshakePackEntry> resolved_packs; /* ordered */

    u64 timestamp_monotonic_us;
    u32 has_timestamp_wall_us; /* 0/1 */
    u64 timestamp_wall_us;     /* valid when has_timestamp_wall_us==1 */

    LauncherHandshake();
};

bool launcher_handshake_to_tlv_bytes(const LauncherHandshake& hs,
                                     std::vector<unsigned char>& out_bytes);
bool launcher_handshake_from_tlv_bytes(const unsigned char* data,
                                       size_t size,
                                       LauncherHandshake& out_hs);

/* Stable hash computed over canonical TLV bytes (FNV-1a 64). */
u64 launcher_handshake_hash64(const LauncherHandshake& hs);

/* Launcher-side refusal codes used by tests and stub validators. */
enum LauncherHandshakeRefusalCode {
    LAUNCHER_HANDSHAKE_REFUSAL_OK = 0u,
    LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS = 1u,
    LAUNCHER_HANDSHAKE_REFUSAL_MANIFEST_HASH_MISMATCH = 2u,
    LAUNCHER_HANDSHAKE_REFUSAL_MISSING_SIM_AFFECTING_PACK_DECLARATIONS = 3u,
    LAUNCHER_HANDSHAKE_REFUSAL_PACK_HASH_MISMATCH = 4u,
    LAUNCHER_HANDSHAKE_REFUSAL_PRELAUNCH_VALIDATION_FAILED = 5u
};

/* Validates a parsed handshake against a manifest and the artifact store.
 * This mirrors expected engine-side refusal behavior (subset used by prompt).
 *
 * Notes:
 * - Uses pack resolution to determine sim-affecting flags deterministically.
 * - Unknown tags are ignored.
 */
u32 launcher_handshake_validate(const launcher_services_api_v1* services,
                                const LauncherHandshake& hs,
                                const LauncherInstanceManifest& manifest,
                                const std::string& state_root_override,
                                std::string* out_detail);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_HANDSHAKE_H */
