/*
FILE: source/dominium/setup/os/cpm/setup_cpm80.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/os/cpm/setup_cpm80
RESPONSIBILITY: Implements `setup_cpm80`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

int main(int argc, char** argv)
{
    (void)argc;
    (void)argv;
    printf("Dominium CP/M-80 installer stub.\n");
    printf("TODO: prompt for target drive/user and copy COM files; create SUBMIT script.\n");
    return 0;
}
