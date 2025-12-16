/*
FILE: external/xxhash/xxhash.h
MODULE: External (third-party)
LAYER / SUBSYSTEM: external/xxhash
RESPONSIBILITY: Vendored third-party source for `xxhash.h`; keep changes minimal and non-functional.
ALLOWED DEPENDENCIES: As shipped by upstream; project-local wrappers may include this.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Upstream versioning applies; see `docs/DEPENDENCIES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_EXTERNAL_XXHASH_H
#define DOMINIUM_EXTERNAL_XXHASH_H

#include <stddef.h>
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

u64 dom_xxhash64(const void* data, size_t len, u64 seed);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_EXTERNAL_XXHASH_H */

