/*
FILE: source/dominium/launcher/core/include/launcher_artifact_store.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / artifact_store
RESPONSIBILITY: Hash-addressed artifact store reader + verification and artifact metadata TLV schema (skip-unknown; deterministic).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core TLV helpers and services facade.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Path construction and serialization are explicit; no filesystem enumeration ordering is relied upon.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_ARTIFACT_STORE_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_ARTIFACT_STORE_H

#include <string>
#include <vector>

extern "C" {
#include "launcher_core_api.h"
}

#include "dominium/core_err.h"

#include "launcher_instance.h"

namespace dom {
namespace launcher_core {

/* Artifact metadata TLV schema version (artifact.tlv). */
enum { LAUNCHER_ARTIFACT_METADATA_TLV_VERSION = 1u };

/* artifact.tlv root records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32): must be `LAUNCHER_ARTIFACT_METADATA_TLV_VERSION`
 * - `LAUNCHER_ARTIFACT_TLV_TAG_HASH_BYTES` (bytes): content hash (sha256 for this prompt)
 * - `LAUNCHER_ARTIFACT_TLV_TAG_SIZE_BYTES` (u64): payload size in bytes
 * - `LAUNCHER_ARTIFACT_TLV_TAG_CONTENT_TYPE` (u32; `LauncherContentType`)
 * - `LAUNCHER_ARTIFACT_TLV_TAG_TIMESTAMP_US` (u64): creation/import timestamp
 * - `LAUNCHER_ARTIFACT_TLV_TAG_VERIFICATION_STATUS` (u32): 0 unknown, 1 verified, 2 failed
 * - `LAUNCHER_ARTIFACT_TLV_TAG_SOURCE` (string, optional): opaque provenance/source
 *
 * Unknown tags must be skipped and preserved when re-encoding.
 */
enum LauncherArtifactMetadataTlvTag {
    LAUNCHER_ARTIFACT_TLV_TAG_HASH_BYTES = 2u,
    LAUNCHER_ARTIFACT_TLV_TAG_SIZE_BYTES = 3u,
    LAUNCHER_ARTIFACT_TLV_TAG_CONTENT_TYPE = 4u,
    LAUNCHER_ARTIFACT_TLV_TAG_TIMESTAMP_US = 5u,
    LAUNCHER_ARTIFACT_TLV_TAG_VERIFICATION_STATUS = 6u,
    LAUNCHER_ARTIFACT_TLV_TAG_SOURCE = 7u
};

enum LauncherArtifactVerificationStatus {
    LAUNCHER_ARTIFACT_VERIFY_UNKNOWN = 0u,
    LAUNCHER_ARTIFACT_VERIFY_VERIFIED = 1u,
    LAUNCHER_ARTIFACT_VERIFY_FAILED = 2u
};

struct LauncherArtifactMetadata {
    u32 schema_version;

    std::vector<unsigned char> hash_bytes;
    u64 size_bytes;
    u32 content_type;
    u64 timestamp_us;
    u32 verification_status;
    std::string source;

    std::vector<LauncherTlvUnknownRecord> unknown_fields;

    LauncherArtifactMetadata();
};

bool launcher_artifact_metadata_to_tlv_bytes(const LauncherArtifactMetadata& meta,
                                             std::vector<unsigned char>& out_bytes);
bool launcher_artifact_metadata_from_tlv_bytes(const unsigned char* data,
                                               size_t size,
                                               LauncherArtifactMetadata& out_meta);

/* Artifact store layout (read-only for instance operations):
 *
 * <state_root>/artifacts/<algo>/<hash_hex>/
 *   artifact.tlv
 *   payload/payload.bin
 */
const char* launcher_artifact_store_default_algo(void); /* returns "sha256" */
const char* launcher_artifact_store_payload_filename(void); /* returns "payload.bin" */

/* Resolves store paths for a hash (no filesystem access). */
bool launcher_artifact_store_paths(const std::string& state_root,
                                   const std::vector<unsigned char>& hash_bytes,
                                   std::string& out_artifact_dir,
                                   std::string& out_metadata_path,
                                   std::string& out_payload_path);

/* Reads and decodes artifact.tlv for the given hash. */
bool launcher_artifact_store_read_metadata(const launcher_services_api_v1* services,
                                           const std::string& state_root_override,
                                           const std::vector<unsigned char>& hash_bytes,
                                           LauncherArtifactMetadata& out_meta);
bool launcher_artifact_store_read_metadata_ex(const launcher_services_api_v1* services,
                                              const std::string& state_root_override,
                                              const std::vector<unsigned char>& hash_bytes,
                                              LauncherArtifactMetadata& out_meta,
                                              err_t* out_err);

/* Verifies that:
 * - artifact.tlv exists and matches the expected hash bytes
 * - payload exists at the canonical path and SHA-256(payload) matches the hash
 * - payload size matches metadata size (when metadata size != 0)
 * - content_type matches expected_content_type when expected_content_type != LAUNCHER_CONTENT_UNKNOWN
 *
 * Returns false on any mismatch or missing files.
 */
bool launcher_artifact_store_verify(const launcher_services_api_v1* services,
                                    const std::string& state_root_override,
                                    const std::vector<unsigned char>& expected_hash_bytes,
                                    u32 expected_content_type,
                                    LauncherArtifactMetadata& out_meta);
bool launcher_artifact_store_verify_ex(const launcher_services_api_v1* services,
                                       const std::string& state_root_override,
                                       const std::vector<unsigned char>& expected_hash_bytes,
                                       u32 expected_content_type,
                                       LauncherArtifactMetadata& out_meta,
                                       err_t* out_err);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_ARTIFACT_STORE_H */
