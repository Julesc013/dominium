/*
FILE: source/domino/system/core/base/dom_core/dom_core_version.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_version
RESPONSIBILITY: Defines internal contract for `dom_core_version`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_CORE_VERSION_H
#define DOM_CORE_VERSION_H

#include "dom_core_types.h"
#include "dom_build_version.h"

/* Runtime accessors for semantic version + global build number. */
const char *dom_version_semver(void);
const char *dom_version_full(void);
dom_u32 dom_version_build_number(void);

#endif /* DOM_CORE_VERSION_H */
