/*
FILE: include/dominium/_internal/dom_priv/dom_shared/uuid.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_shared/uuid
RESPONSIBILITY: Defines internal contract for UUID string generation helper; not a stable public API; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal header; output is a human-oriented identifier string, not a stable protocol.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SHARED_UUID_H
#define DOM_SHARED_UUID_H

#include <string>

namespace dom_shared {

/* Purpose: Generate a pseudo-random UUIDv4-like identifier string.
 *
 * Returns:
 * - Lowercase hex string in the form `"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"`.
 *
 * Determinism:
 * - Non-deterministic: current implementation seeds `std::rand()` from wall-clock time on first use.
 * - Must not be used by deterministic simulation code paths (see `docs/SPEC_DETERMINISM.md`).
 *
 * Thread-safety:
 * - Not thread-safe (lazy seeding without synchronization).
 *
 * Security:
 * - Not cryptographically secure; do not use for secrets.
 */
std::string generate_uuid();

} // namespace dom_shared

#endif
