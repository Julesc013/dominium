/*
FILE: source/dominium/tools/modcheck/dom_modcheck_main.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/modcheck/dom_modcheck_main
RESPONSIBILITY: Implements `dom_modcheck_main`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>

#include "dom_modcheck.h"

int main(int argc, char **argv) {
    if (argc < 2) {
        std::printf("Usage: modcheck <mod-path>\n");
        return 1;
    }

    const char *path = argv[1];
    return dom::modcheck_run(path) ? 0 : 1;
}
