/*
FILE: include/dominium/dom_plat.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / dom_plat
RESPONSIBILITY: Defines the public contract for `dom_plat` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_PLATFORM_H
#define DOM_PLATFORM_H

/* Purpose: Backward-compatible include shim for legacy Dominium code.
 *
 * Notes:
 * - Platform enums and selectors live in `domino/platform.h`; prefer including that header directly.
 */
#include "domino/platform.h"

#endif /* DOM_PLATFORM_H */
