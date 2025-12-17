/*
FILE: source/domino/core/dom_build_info.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dom_build_info
RESPONSIBILITY: Implements `dom_build_info`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/build_info.h"
#include "domino/config_base.h"

static const dom_build_info_v1 g_dom_build_info_v1 = {
    DOM_ABI_HEADER_INIT(DOM_BUILD_INFO_ABI_VERSION, dom_build_info_v1),
    DOM_BUILD_ID,
    DOM_GIT_HASH,
    1u,
    1u,
    DOM_PROFILE_BASELINE,
    0u
};

const dom_build_info_v1* dom_build_info_v1_get(void)
{
    return &g_dom_build_info_v1;
}

const char* dom_build_id(void)
{
    return g_dom_build_info_v1.build_id;
}

const char* dom_git_hash(void)
{
    return g_dom_build_info_v1.git_hash;
}

const char* dom_toolchain_id(void)
{
    return DOM_TOOLCHAIN_ID;
}
