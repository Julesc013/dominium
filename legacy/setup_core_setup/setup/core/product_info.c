/*
FILE: source/dominium/setup/core/product_info.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/product_info
RESPONSIBILITY: Implements `product_info`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/compat.h"
#include "domino/platform.h"
#include "dominium/product_info.h"
#include "dominium/version.h"

static DomProductInfo g_dominium_setup_product_info = {
    "setup",
    DOM_COMP_ROLE_INSTALLER,
    "setup",
    DOMINIUM_SETUP_VERSION,
    DOMINIUM_CORE_VERSION,
    DOMINIUM_SUITE_VERSION,
    DOM_OSFAM_WIN_NT,
    DOM_ARCH_X86_64,
    DMN_EMPTY_COMPAT_PROFILE
};

static void dmn_init_setup_product_info(void)
{
    static int initialized = 0;
    if (initialized) return;
    g_dominium_setup_product_info.os_family = dominium_detect_os_family();
    g_dominium_setup_product_info.arch = dominium_detect_arch();
    initialized = 1;
}

const DomProductInfo* dom_get_product_info_setup(void)
{
    dmn_init_setup_product_info();
    return &g_dominium_setup_product_info;
}
