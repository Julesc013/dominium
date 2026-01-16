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

/* Purpose: Temporary facade for package/manifest structures used by Dominium tools/launcher.
 *
 * Notes:
 * - This header currently re-exports internal C++98 types and is not a stable C ABI.
 * - A future revision is expected to publish stable POD C structs for package/manifest I/O.
 */
/* TODO: publish stable C structs for package/manifest IO. */
#ifdef __cplusplus
#include "dom_contracts/dom_shared/manifest_install.h"
#else
#error "dom_package_manifest.h currently requires C++ (std::string); refactor to C ABI"
#endif

#endif /* DOMINIUM_DOM_PACKAGE_MANIFEST_H */
