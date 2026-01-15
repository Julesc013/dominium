/*
FILE: source/dominium/launcher/core/include/launcher_instance_payload_refs.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_payload_refs
RESPONSIBILITY: Instance payload-reference index model + TLV persistence (versioned; skip-unknown; deterministic).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core TLV helpers only.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Serialization is canonical; list ordering is explicit and preserved.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_PAYLOAD_REFS_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_PAYLOAD_REFS_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "launcher_instance.h"

namespace dom {
namespace launcher_core {

/* TLV schema version for payload reference root. */
enum { LAUNCHER_INSTANCE_PAYLOAD_REFS_TLV_VERSION = 1u };

/* payload_refs.tlv root records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_INSTANCE_PAYLOAD_REFS_TLV_VERSION`
 * - `LAUNCHER_PAYLOAD_REFS_TLV_TAG_INSTANCE_ID` (string)
 * - `LAUNCHER_PAYLOAD_REFS_TLV_TAG_MANIFEST_HASH64` (u64): manifest hash this index corresponds to
 * - `LAUNCHER_PAYLOAD_REFS_TLV_TAG_ENTRY` (container, repeated): ordered payload references
 *
 * Entry payload (container TLV):
 * - `LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_TYPE` (u32; `LauncherContentType`)
 * - `LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_ID` (string)
 * - `LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_VERSION` (string)
 * - `LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_HASH_BYTES` (bytes)
 * - `LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_SIZE_BYTES` (u64)
 * - `LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_STORE_ALGO` (string)
 */
enum LauncherPayloadRefsTlvTag {
    LAUNCHER_PAYLOAD_REFS_TLV_TAG_INSTANCE_ID = 2u,
    LAUNCHER_PAYLOAD_REFS_TLV_TAG_MANIFEST_HASH64 = 3u,
    LAUNCHER_PAYLOAD_REFS_TLV_TAG_ENTRY = 4u
};

enum LauncherPayloadRefsEntryTlvTag {
    LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_TYPE = 1u,
    LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_ID = 2u,
    LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_VERSION = 3u,
    LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_HASH_BYTES = 4u,
    LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_SIZE_BYTES = 5u,
    LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_STORE_ALGO = 6u
};

struct LauncherPayloadRefEntry {
    u32 type;
    std::string id;
    std::string version;
    std::vector<unsigned char> hash_bytes;
    u64 size_bytes;
    std::string store_algo;

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherPayloadRefEntry();
};

struct LauncherInstancePayloadRefs {
    u32 schema_version;
    std::string instance_id;
    u64 manifest_hash64;
    std::vector<LauncherPayloadRefEntry> entries;

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherInstancePayloadRefs();
};

bool launcher_instance_payload_refs_to_tlv_bytes(const LauncherInstancePayloadRefs& refs,
                                                 std::vector<unsigned char>& out_bytes);
bool launcher_instance_payload_refs_from_tlv_bytes(const unsigned char* data,
                                                   size_t size,
                                                   LauncherInstancePayloadRefs& out_refs);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_PAYLOAD_REFS_H */

