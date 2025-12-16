/*
FILE: source/dominium/launcher/core/include/launcher_instance.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance
RESPONSIBILITY: Launcher instance state model + manifest (lockfile) TLV schema (versioned, skip-unknown).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types only.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: Serialization is canonical and list ordering is explicit and preserved.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "launcher_artifact.h"

namespace dom {
namespace launcher_core {

/* TLV schema version for instance manifest root. */
enum { LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION = 1u };

/* Instance Manifest TLV schema (LOCKFILE; versioned root; skip-unknown).
 *
 * Root TLV records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION`.
 * - `LAUNCHER_INSTANCE_TLV_TAG_INSTANCE_ID` (string)
 * - `LAUNCHER_INSTANCE_TLV_TAG_PIN_ENGINE_BUILD_ID` (string)
 * - `LAUNCHER_INSTANCE_TLV_TAG_PIN_GAME_BUILD_ID` (string)
 * - `LAUNCHER_INSTANCE_TLV_TAG_PINNED_CONTENT_ENTRY` (container, repeated): pinned content/mod entries.
 * - `LAUNCHER_INSTANCE_TLV_TAG_UPDATE_POLICY_FLAGS` (u32)
 * - `LAUNCHER_INSTANCE_TLV_TAG_KNOWN_GOOD` (u32; 0/1)
 *
 * Pinned content entry payload (container TLV):
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_KIND` (u32; `LauncherArtifactKind`)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ID` (string)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_BUILD_ID` (string)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_HASH_BYTES` (bytes)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ORDER` (u32): explicit stable ordering key.
 */
enum LauncherInstanceManifestTlvTag {
    LAUNCHER_INSTANCE_TLV_TAG_INSTANCE_ID = 2u,
    LAUNCHER_INSTANCE_TLV_TAG_PIN_ENGINE_BUILD_ID = 3u,
    LAUNCHER_INSTANCE_TLV_TAG_PIN_GAME_BUILD_ID = 4u,
    LAUNCHER_INSTANCE_TLV_TAG_PINNED_CONTENT_ENTRY = 5u,
    LAUNCHER_INSTANCE_TLV_TAG_UPDATE_POLICY_FLAGS = 6u,
    LAUNCHER_INSTANCE_TLV_TAG_KNOWN_GOOD = 7u
};

enum LauncherInstancePinnedEntryTlvTag {
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_KIND = 1u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ID = 2u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_BUILD_ID = 3u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_HASH_BYTES = 4u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ORDER = 5u
};

struct LauncherPinnedContent {
    LauncherArtifactRef artifact;
    u32 order_index; /* explicit stable ordering key */

    LauncherPinnedContent();
};

struct LauncherInstanceManifest {
    u32 schema_version;

    std::string instance_id;
    std::string pinned_engine_build_id;
    std::string pinned_game_build_id;

    std::vector<LauncherPinnedContent> pinned_content;

    u32 update_policy_flags;
    u32 known_good;

    LauncherInstanceManifest();
};

LauncherInstanceManifest launcher_instance_manifest_make_empty(const std::string& instance_id);
LauncherInstanceManifest launcher_instance_manifest_make_null(void);

bool launcher_instance_manifest_to_tlv_bytes(const LauncherInstanceManifest& manifest,
                                             std::vector<unsigned char>& out_bytes);
bool launcher_instance_manifest_from_tlv_bytes(const unsigned char* data,
                                               size_t size,
                                               LauncherInstanceManifest& out_manifest);

/* Deterministic manifest hash computed over canonical TLV bytes. */
u64 launcher_instance_manifest_hash64(const LauncherInstanceManifest& manifest);

/* Migration hook (defined but not implemented in foundation).
 * Returns false until a future prompt provides migrations.
 */
bool launcher_instance_manifest_migrate_tlv(u32 from_version,
                                            u32 to_version,
                                            const unsigned char* data,
                                            size_t size,
                                            LauncherInstanceManifest& out_manifest);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_H */
