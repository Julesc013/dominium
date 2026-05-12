/*
FILE: source/dominium/launcher/core/include/launcher_pack_manifest.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / pack_manifest
RESPONSIBILITY: Pack manifest TLV schema + deterministic encode/decode (versioned, skip-unknown, forward-compatible).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core TLV helpers and unknown-record model.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Serialization is canonical; list ordering is explicitly defined and stable.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_MANIFEST_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_MANIFEST_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "launcher_instance.h" /* LauncherTlvUnknownRecord */

namespace dom {
namespace launcher_core {

/* TLV schema version for pack manifest root. */
enum { LAUNCHER_PACK_MANIFEST_TLV_VERSION = 1u };

/* pack_manifest.tlv schema (versioned root; skip-unknown; forward-compatible).
 *
 * Root required fields:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_PACK_MANIFEST_TLV_VERSION`
 * - `LAUNCHER_PACK_TLV_TAG_PACK_ID` (string)
 * - `LAUNCHER_PACK_TLV_TAG_PACK_TYPE` (u32; `LauncherPackType`)
 * - `LAUNCHER_PACK_TLV_TAG_VERSION` (string)
 * - `LAUNCHER_PACK_TLV_TAG_PACK_HASH_BYTES` (bytes)
 * - `LAUNCHER_PACK_TLV_TAG_COMPAT_ENGINE_RANGE` (container; `LauncherPackVersionRange`)
 * - `LAUNCHER_PACK_TLV_TAG_COMPAT_GAME_RANGE` (container; `LauncherPackVersionRange`)
 *
 * Dependency graph (containers, repeated):
 * - `LAUNCHER_PACK_TLV_TAG_REQUIRED_DEP` (container; `LauncherPackDepEntry`)
 * - `LAUNCHER_PACK_TLV_TAG_OPTIONAL_DEP` (container; `LauncherPackDepEntry`)
 * - `LAUNCHER_PACK_TLV_TAG_CONFLICT` (container; `LauncherPackDepEntry`)
 *
 * Load order metadata (optional):
 * - `LAUNCHER_PACK_TLV_TAG_PHASE` (u32; `LauncherPackPhase`; default NORMAL)
 * - `LAUNCHER_PACK_TLV_TAG_EXPLICIT_ORDER` (i32; default 0)
 *
 * Feature flags:
 * - `LAUNCHER_PACK_TLV_TAG_CAPABILITY` (string, repeated)
 * - `LAUNCHER_PACK_TLV_TAG_SIM_FLAG` (string, repeated; must be declared as a capability)
 *
 * Declarative tasks (containers, repeated):
 * - `LAUNCHER_PACK_TLV_TAG_INSTALL_TASK` (container; `LauncherPackTask`)
 * - `LAUNCHER_PACK_TLV_TAG_VERIFY_TASK` (container; `LauncherPackTask`)
 * - `LAUNCHER_PACK_TLV_TAG_PRELAUNCH_TASK` (container; `LauncherPackTask`)
 */
enum LauncherPackManifestTlvTag {
    LAUNCHER_PACK_TLV_TAG_PACK_ID = 2u,
    LAUNCHER_PACK_TLV_TAG_PACK_TYPE = 3u,
    LAUNCHER_PACK_TLV_TAG_VERSION = 4u,
    LAUNCHER_PACK_TLV_TAG_PACK_HASH_BYTES = 5u,
    LAUNCHER_PACK_TLV_TAG_COMPAT_ENGINE_RANGE = 6u,
    LAUNCHER_PACK_TLV_TAG_COMPAT_GAME_RANGE = 7u,

    LAUNCHER_PACK_TLV_TAG_REQUIRED_DEP = 8u,
    LAUNCHER_PACK_TLV_TAG_OPTIONAL_DEP = 9u,
    LAUNCHER_PACK_TLV_TAG_CONFLICT = 10u,

    LAUNCHER_PACK_TLV_TAG_PHASE = 11u,
    LAUNCHER_PACK_TLV_TAG_EXPLICIT_ORDER = 12u,

    LAUNCHER_PACK_TLV_TAG_CAPABILITY = 13u,
    LAUNCHER_PACK_TLV_TAG_SIM_FLAG = 14u,

    LAUNCHER_PACK_TLV_TAG_INSTALL_TASK = 15u,
    LAUNCHER_PACK_TLV_TAG_VERIFY_TASK = 16u,
    LAUNCHER_PACK_TLV_TAG_PRELAUNCH_TASK = 17u
};

enum LauncherPackType {
    LAUNCHER_PACK_TYPE_CONTENT = 1u,
    LAUNCHER_PACK_TYPE_MOD = 2u,
    LAUNCHER_PACK_TYPE_RUNTIME = 3u
};

enum LauncherPackPhase {
    LAUNCHER_PACK_PHASE_EARLY = 1u,
    LAUNCHER_PACK_PHASE_NORMAL = 2u,
    LAUNCHER_PACK_PHASE_LATE = 3u
};

/* Version range container:
 * - `LAUNCHER_PACK_RANGE_TLV_TAG_MIN` (string, optional)
 * - `LAUNCHER_PACK_RANGE_TLV_TAG_MAX` (string, optional)
 */
enum LauncherPackVersionRangeTlvTag {
    LAUNCHER_PACK_RANGE_TLV_TAG_MIN = 1u,
    LAUNCHER_PACK_RANGE_TLV_TAG_MAX = 2u
};

struct LauncherPackVersionRange {
    std::string min_version; /* inclusive; empty when absent */
    std::string max_version; /* inclusive; empty when absent */

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherPackVersionRange();
};

/* Dependency entry container:
 * - `LAUNCHER_PACK_DEP_TLV_TAG_ID` (string)
 * - `LAUNCHER_PACK_DEP_TLV_TAG_RANGE` (container; `LauncherPackVersionRange`)
 */
enum LauncherPackDepEntryTlvTag {
    LAUNCHER_PACK_DEP_TLV_TAG_ID = 1u,
    LAUNCHER_PACK_DEP_TLV_TAG_RANGE = 2u
};

struct LauncherPackDependency {
    std::string pack_id;
    LauncherPackVersionRange version_range;

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherPackDependency();
};

enum LauncherPackTaskKind {
    /* Read-only: require a file to exist under the instance root. */
    LAUNCHER_PACK_TASK_REQUIRE_FILE = 1u
};

/* Task container:
 * - `LAUNCHER_PACK_TASK_TLV_TAG_KIND` (u32; `LauncherPackTaskKind`)
 * - `LAUNCHER_PACK_TASK_TLV_TAG_PATH` (string)
 */
enum LauncherPackTaskTlvTag {
    LAUNCHER_PACK_TASK_TLV_TAG_KIND = 1u,
    LAUNCHER_PACK_TASK_TLV_TAG_PATH = 2u
};

struct LauncherPackTask {
    u32 kind;
    std::string path; /* instance-relative path; must not escape instance root */

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherPackTask();
};

struct LauncherPackManifest {
    u32 schema_version;

    std::string pack_id;
    u32 pack_type;
    std::string version;
    std::vector<unsigned char> pack_hash_bytes;

    LauncherPackVersionRange compatible_engine_range;
    LauncherPackVersionRange compatible_game_range;
    u32 has_compatible_engine_range; /* 0/1 */
    u32 has_compatible_game_range;   /* 0/1 */

    std::vector<LauncherPackDependency> required_packs;
    std::vector<LauncherPackDependency> optional_packs;
    std::vector<LauncherPackDependency> conflicts;

    u32 phase; /* `LauncherPackPhase` */
    i32 explicit_order;

    std::vector<std::string> declared_capabilities;
    std::vector<std::string> sim_affecting_flags;

    std::vector<LauncherPackTask> install_tasks;
    std::vector<LauncherPackTask> verify_tasks;
    std::vector<LauncherPackTask> prelaunch_tasks;

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherPackManifest();
};

bool launcher_pack_manifest_to_tlv_bytes(const LauncherPackManifest& manifest,
                                         std::vector<unsigned char>& out_bytes);
bool launcher_pack_manifest_from_tlv_bytes(const unsigned char* data,
                                           size_t size,
                                           LauncherPackManifest& out_manifest);

/* Validates required fields and safety invariants (e.g., sim flags must be declared). */
bool launcher_pack_manifest_validate(const LauncherPackManifest& manifest,
                                     std::string* out_error);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_MANIFEST_H */
