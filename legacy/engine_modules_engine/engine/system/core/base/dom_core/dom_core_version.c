/*
FILE: source/domino/system/core/base/dom_core/dom_core_version.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_version
RESPONSIBILITY: Implements `dom_core_version`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_core_version.h"

const char *dom_version_semver(void)
{
    return DOM_VERSION_SEMVER;
}

const char *dom_version_full(void)
{
    return DOM_VERSION_BUILD_STR;
}

dom_u32 dom_version_build_number(void)
{
    return (dom_u32)DOM_BUILD_NUMBER;
}
