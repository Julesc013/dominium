/*
FILE: include/dominium/dom_package_manifest.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / dom_package_manifest
RESPONSIBILITY: Defines the public contract for `dom_package_manifest` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_DOM_PACKAGE_MANIFEST_H
#define DOMINIUM_DOM_PACKAGE_MANIFEST_H

extern "C" {
#include "domino/core/types.h"
}

/* Purpose: Temporary facade for package/manifest structures used by Dominium tools/launcher.
 *
 * Notes:
 * - This header now exposes a minimal POD placeholder until a stable ABI is published.
 * - Use tool-specific schemas for actual manifest content.
 */
typedef struct dom_package_manifest {
    u32 struct_size;
    u32 struct_version;
} dom_package_manifest;

#endif /* DOMINIUM_DOM_PACKAGE_MANIFEST_H */
