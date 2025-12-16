/*
FILE: source/dominium/launcher/core/include/launcher_instance.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance
RESPONSIBILITY: Launcher instance state model + manifest (lockfile) TLV schema (versioned, skip-unknown, round-trip preserving).
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

namespace dom {
namespace launcher_core {

/* TLV schema version for instance manifest root. */
enum { LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION = 2u };

/* Instance Manifest TLV schema (LOCKFILE; versioned root; skip-unknown).
 *
 * Root TLV records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION`.
 * - `LAUNCHER_INSTANCE_TLV_TAG_INSTANCE_ID` (string): stable instance identifier (UUID/string).
 * - `LAUNCHER_INSTANCE_TLV_TAG_CREATION_TIMESTAMP_US` (u64): creation time (monotonic microseconds).
 * - `LAUNCHER_INSTANCE_TLV_TAG_PIN_ENGINE_BUILD_ID` (string): pinned engine build id.
 * - `LAUNCHER_INSTANCE_TLV_TAG_PIN_GAME_BUILD_ID` (string): pinned game build id.
 * - `LAUNCHER_INSTANCE_TLV_TAG_CONTENT_ENTRY` (container, repeated): ordered content graph entries.
 * - `LAUNCHER_INSTANCE_TLV_TAG_KNOWN_GOOD` (u32; 0/1): known-good marker.
 * - `LAUNCHER_INSTANCE_TLV_TAG_LAST_VERIFIED_TIMESTAMP_US` (u64): last verification time.
 * - `LAUNCHER_INSTANCE_TLV_TAG_PREVIOUS_MANIFEST_HASH64` (u64, optional): previous manifest hash for provenance.
 * - `LAUNCHER_INSTANCE_TLV_TAG_PROVENANCE_SOURCE_INSTANCE_ID` (string, optional): source instance_id for clones/imports.
 * - `LAUNCHER_INSTANCE_TLV_TAG_PROVENANCE_SOURCE_MANIFEST_HASH64` (u64, optional): source manifest hash for clones/imports.
 *
 * Content entry payload (container TLV):
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_TYPE` (u32; `LauncherContentType`)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ID` (string)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_VERSION` (string)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_HASH_BYTES` (bytes)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ENABLED` (u32; 0/1)
 * - `LAUNCHER_INSTANCE_ENTRY_TLV_TAG_UPDATE_POLICY` (u32; `LauncherUpdatePolicy`)
 */
enum LauncherInstanceManifestTlvTag {
    LAUNCHER_INSTANCE_TLV_TAG_INSTANCE_ID = 2u,
    LAUNCHER_INSTANCE_TLV_TAG_PIN_ENGINE_BUILD_ID = 3u,
    LAUNCHER_INSTANCE_TLV_TAG_PIN_GAME_BUILD_ID = 4u,
    /* tag 5 was used by v1 pinned-content entries */
    /* tag 6 was used by v1 update_policy_flags */
    LAUNCHER_INSTANCE_TLV_TAG_KNOWN_GOOD = 7u,
    LAUNCHER_INSTANCE_TLV_TAG_CREATION_TIMESTAMP_US = 8u,
    LAUNCHER_INSTANCE_TLV_TAG_LAST_VERIFIED_TIMESTAMP_US = 9u,
    LAUNCHER_INSTANCE_TLV_TAG_PREVIOUS_MANIFEST_HASH64 = 10u,
    LAUNCHER_INSTANCE_TLV_TAG_CONTENT_ENTRY = 11u,
    LAUNCHER_INSTANCE_TLV_TAG_PROVENANCE_SOURCE_INSTANCE_ID = 12u,
    LAUNCHER_INSTANCE_TLV_TAG_PROVENANCE_SOURCE_MANIFEST_HASH64 = 13u
};

enum LauncherInstancePinnedEntryTlvTag {
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_TYPE = 1u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ID = 2u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_VERSION = 3u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_HASH_BYTES = 4u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ENABLED = 5u,
    LAUNCHER_INSTANCE_ENTRY_TLV_TAG_UPDATE_POLICY = 6u
};

enum LauncherContentType {
    LAUNCHER_CONTENT_UNKNOWN = 0u,
    LAUNCHER_CONTENT_ENGINE = 1u,
    LAUNCHER_CONTENT_GAME = 2u,
    LAUNCHER_CONTENT_PACK = 3u,
    LAUNCHER_CONTENT_MOD = 4u,
    LAUNCHER_CONTENT_RUNTIME = 5u
};

enum LauncherUpdatePolicy {
    LAUNCHER_UPDATE_NEVER = 0u,
    LAUNCHER_UPDATE_PROMPT = 1u,
    LAUNCHER_UPDATE_AUTO = 2u
};

struct LauncherTlvUnknownRecord {
    u32 tag;
    std::vector<unsigned char> payload;

    LauncherTlvUnknownRecord();
};

struct LauncherContentEntry {
    u32 type;
    std::string id;
    std::string version;
    std::vector<unsigned char> hash_bytes;
    u32 enabled;
    u32 update_policy;

    /* Unknown fields inside the entry container (round-trip preserved). */
    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherContentEntry();
};

struct LauncherInstanceManifest {
    u32 schema_version;

    std::string instance_id;
    u64 creation_timestamp_us;
    std::string pinned_engine_build_id;
    std::string pinned_game_build_id;

    /* Ordered content graph entries. */
    std::vector<LauncherContentEntry> content_entries;

    /* State markers. */
    u32 known_good; /* 0/1 */
    u64 last_verified_timestamp_us;
    u64 previous_manifest_hash64; /* 0 when absent */

    /* Provenance (optional). */
    std::string provenance_source_instance_id;
    u64 provenance_source_manifest_hash64; /* 0 when absent */

    /* Unknown root fields (round-trip preserved). */
    std::vector<LauncherTlvUnknownRecord> unknown_fields;

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
