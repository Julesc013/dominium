/*
FILE: source/dominium/launcher/core/include/launcher_tlv_migrations.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tlv
RESPONSIBILITY: Central registry for launcher TLV schemas: current versions, minimum supported versions, and migration hooks.
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core TLV schema headers.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: Stateless; safe for concurrent reads.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Pure lookups; no hidden time or filesystem access.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_MIGRATIONS_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_MIGRATIONS_H

#include <stddef.h>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace launcher_core {

/* Stable IDs for TLV schemas used by launcher core.
 * These IDs are for registry lookup and diagnostics only; they do not appear on disk.
 */
enum LauncherTlvSchemaId {
    LAUNCHER_TLV_SCHEMA_UNKNOWN = 0u,

    LAUNCHER_TLV_SCHEMA_AUDIT_LOG = 1u,
    LAUNCHER_TLV_SCHEMA_PROFILE = 2u,

    LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST = 3u,
    LAUNCHER_TLV_SCHEMA_INSTANCE_CONFIG = 4u,
    LAUNCHER_TLV_SCHEMA_INSTANCE_KNOWN_GOOD = 5u,
    LAUNCHER_TLV_SCHEMA_INSTANCE_LAUNCH_HISTORY = 6u,
    LAUNCHER_TLV_SCHEMA_INSTANCE_PAYLOAD_REFS = 7u,
    LAUNCHER_TLV_SCHEMA_INSTANCE_TX = 8u,

    LAUNCHER_TLV_SCHEMA_ARTIFACT_METADATA = 9u,
    LAUNCHER_TLV_SCHEMA_PACK_MANIFEST = 10u,

    LAUNCHER_TLV_SCHEMA_RESOLVED_LAUNCH_CONFIG = 11u
};

struct LauncherTlvSchemaSpec {
    u32 schema_id; /* LauncherTlvSchemaId */
    const char* name;
    u32 min_version;
    u32 current_version;
};

typedef bool (*launcher_tlv_migrate_bytes_fn)(u32 from_version,
                                              u32 to_version,
                                              const unsigned char* data,
                                              size_t size,
                                              std::vector<unsigned char>& out_bytes);

/* Registry queries. */
size_t launcher_tlv_schema_count(void);
const LauncherTlvSchemaSpec* launcher_tlv_schema_at(size_t index);
const LauncherTlvSchemaSpec* launcher_tlv_schema_find(u32 schema_id);

const char* launcher_tlv_schema_name(u32 schema_id);
u32 launcher_tlv_schema_min_version(u32 schema_id);
u32 launcher_tlv_schema_current_version(u32 schema_id);

/* Version guard: returns true only if the given on-disk schema version is supported
 * by this build (either native/current or migratable to current).
 */
bool launcher_tlv_schema_accepts_version(u32 schema_id, u32 disk_version);

/* Migration dispatch (bytes-in -> bytes-out) for schemas that support it.
 * Returns false when migration is impossible or not implemented for the schema.
 */
bool launcher_tlv_schema_migrate_bytes(u32 schema_id,
                                       u32 from_version,
                                       u32 to_version,
                                       const unsigned char* data,
                                       size_t size,
                                       std::vector<unsigned char>& out_bytes);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_MIGRATIONS_H */

