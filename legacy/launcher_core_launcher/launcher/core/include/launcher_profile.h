/*
FILE: source/dominium/launcher/core/include/launcher_profile.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / profile
RESPONSIBILITY: Launcher profile state model + TLV persistence schema (versioned, skip-unknown).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types only; no OS/UI headers.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Serialization is canonical and order-preserving; unknown tags are skipped.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_PROFILE_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_PROFILE_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace launcher_core {

/* TLV schema version for launcher profile root. */
enum { LAUNCHER_PROFILE_TLV_VERSION = 1u };

/* Launcher Profile TLV schema (versioned root; skip-unknown).
 *
 * Root TLV records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_PROFILE_TLV_VERSION`.
 * - `LAUNCHER_PROFILE_TLV_TAG_PROFILE_ID` (string): profile identifier.
 * - `LAUNCHER_PROFILE_TLV_TAG_ALLOWED_BACKEND` (container, repeated): allowed subsystem/backend pairs.
 * - `LAUNCHER_PROFILE_TLV_TAG_POLICY_FLAGS` (u32): launcher policy bitset (future-defined).
 * - `LAUNCHER_PROFILE_TLV_TAG_DET_CONSTRAINTS` (u32): determinism constraint bitset (future-defined).
 *
 * Allowed-backend entry payload (container TLV):
 * - `LAUNCHER_PROFILE_ALLOW_TLV_TAG_SUBSYSTEM_KEY` (string)
 * - `LAUNCHER_PROFILE_ALLOW_TLV_TAG_BACKEND_NAME` (string)
 */
enum LauncherProfileTlvTag {
    LAUNCHER_PROFILE_TLV_TAG_PROFILE_ID = 2u,
    LAUNCHER_PROFILE_TLV_TAG_ALLOWED_BACKEND = 3u,
    LAUNCHER_PROFILE_TLV_TAG_POLICY_FLAGS = 4u,
    LAUNCHER_PROFILE_TLV_TAG_DET_CONSTRAINTS = 5u
};

enum LauncherProfileAllowedBackendTlvTag {
    LAUNCHER_PROFILE_ALLOW_TLV_TAG_SUBSYSTEM_KEY = 1u,
    LAUNCHER_PROFILE_ALLOW_TLV_TAG_BACKEND_NAME = 2u
};

struct LauncherBackendAllow {
    std::string subsystem_key;
    std::string backend_name;
};

struct LauncherProfile {
    u32 schema_version;

    std::string profile_id;
    std::vector<LauncherBackendAllow> allowed_backends;

    u32 policy_flags;
    u32 determinism_constraints;

    LauncherProfile();
};

LauncherProfile launcher_profile_make_null(void);

bool launcher_profile_to_tlv_bytes(const LauncherProfile& profile,
                                   std::vector<unsigned char>& out_bytes);
bool launcher_profile_from_tlv_bytes(const unsigned char* data,
                                     size_t size,
                                     LauncherProfile& out_profile);

/* Migration hook (defined but not implemented in foundation).
 * Returns false until a future prompt provides migrations.
 */
bool launcher_profile_migrate_tlv(u32 from_version,
                                  u32 to_version,
                                  const unsigned char* data,
                                  size_t size,
                                  LauncherProfile& out_profile);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_PROFILE_H */
