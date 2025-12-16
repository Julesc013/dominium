/*
FILE: source/dominium/game/cli/server/dom_server_main.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/cli/server/dom_server_main
RESPONSIBILITY: Implements `dom_server_main`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "dom_core_version.h"

int main(void)
{
    printf("dom_server %s (build %u) stub\n",
           dom_version_full(),
           (unsigned)dom_version_build_number());
    return 0;
}
