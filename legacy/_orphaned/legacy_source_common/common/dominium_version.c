/*
FILE: source/dominium/common/dominium_version.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dominium_version
RESPONSIBILITY: Implements `dominium_version`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/version.h"

void dominium_game_get_version(domino_semver* out)
{
    if (!out) return;
    domino_semver_parse(DOMINIUM_GAME_VERSION, out);
}

void dominium_launcher_get_version(domino_semver* out)
{
    if (!out) return;
    domino_semver_parse(DOMINIUM_LAUNCHER_VERSION, out);
}

const char* dominium_get_core_version_string(void)
{
    return DOMINIUM_CORE_VERSION;
}

const char* dominium_get_game_version_string(void)
{
    return DOMINIUM_GAME_VERSION;
}

const char* dominium_get_launcher_version_string(void)
{
    return DOMINIUM_LAUNCHER_VERSION;
}

const char* dominium_get_setup_version_string(void)
{
    return DOMINIUM_SETUP_VERSION;
}

const char* dominium_get_tools_version_string(void)
{
    return DOMINIUM_TOOLS_VERSION;
}

const char* dominium_get_suite_version_string(void)
{
    return DOMINIUM_SUITE_VERSION;
}

int dominium_game_get_content_api(void)
{
    return 1;
}

int dominium_launcher_get_content_api(void)
{
    return 1;
}

int dominium_launcher_get_ext_api(void)
{
    return 1;
}
