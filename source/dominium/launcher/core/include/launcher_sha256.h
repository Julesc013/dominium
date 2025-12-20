/*
FILE: source/dominium/launcher/core/include/launcher_sha256.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / sha256
RESPONSIBILITY: Minimal SHA-256 implementation for content-addressing and verification (no OS headers; deterministic).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher services facade types.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Pure functions over explicit inputs; stable across platforms.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_SHA256_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_SHA256_H

#include <stddef.h>
#include <string>
#include <vector>

extern "C" {
#include "launcher_core_api.h"
}

namespace dom {
namespace launcher_core {

enum { LAUNCHER_SHA256_BYTES = 32u };

/* Computes SHA-256 over a byte buffer. */
void launcher_sha256_bytes(const unsigned char* data,
                           size_t size,
                           unsigned char out_hash[LAUNCHER_SHA256_BYTES]);

/* Streams a file through SHA-256 using the launcher FS facade.
 * Returns false if the file cannot be read.
 */
bool launcher_sha256_file(const launcher_services_api_v1* services,
                          const std::string& path,
                          std::vector<unsigned char>& out_hash_bytes,
                          u64& out_size_bytes);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_SHA256_H */

