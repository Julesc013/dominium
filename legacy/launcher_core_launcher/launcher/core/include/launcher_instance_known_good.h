/*
FILE: source/dominium/launcher/core/include/launcher_instance_known_good.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_known_good
RESPONSIBILITY: Last-known-good pointer model + TLV persistence (versioned; skip-unknown; deterministic).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core TLV helpers only.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Serialization is canonical; no filesystem enumeration ordering is relied upon.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_KNOWN_GOOD_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_KNOWN_GOOD_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "launcher_instance.h"

namespace dom {
namespace launcher_core {

/* TLV schema version for known-good pointer root. */
enum { LAUNCHER_INSTANCE_KNOWN_GOOD_TLV_VERSION = 1u };

/* known_good.tlv root records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32)
 * - `LAUNCHER_KNOWN_GOOD_TLV_TAG_INSTANCE_ID` (string)
 * - `LAUNCHER_KNOWN_GOOD_TLV_TAG_PREVIOUS_DIR` (string): relative directory under `previous/`
 * - `LAUNCHER_KNOWN_GOOD_TLV_TAG_MANIFEST_HASH64` (u64)
 * - `LAUNCHER_KNOWN_GOOD_TLV_TAG_TIMESTAMP_US` (u64): when pointer was set
 */
enum LauncherKnownGoodTlvTag {
    LAUNCHER_KNOWN_GOOD_TLV_TAG_INSTANCE_ID = 2u,
    LAUNCHER_KNOWN_GOOD_TLV_TAG_PREVIOUS_DIR = 3u,
    LAUNCHER_KNOWN_GOOD_TLV_TAG_MANIFEST_HASH64 = 4u,
    LAUNCHER_KNOWN_GOOD_TLV_TAG_TIMESTAMP_US = 5u
};

struct LauncherInstanceKnownGoodPointer {
    u32 schema_version;
    std::string instance_id;
    std::string previous_dir;
    u64 manifest_hash64;
    u64 timestamp_us;

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherInstanceKnownGoodPointer();
};

bool launcher_instance_known_good_to_tlv_bytes(const LauncherInstanceKnownGoodPointer& kg,
                                               std::vector<unsigned char>& out_bytes);
bool launcher_instance_known_good_from_tlv_bytes(const unsigned char* data,
                                                 size_t size,
                                                 LauncherInstanceKnownGoodPointer& out_kg);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_KNOWN_GOOD_H */

