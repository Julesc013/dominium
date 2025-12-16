/*
FILE: source/dominium/setup/os/carbon/setup_carbon.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/os/carbon/setup_carbon
RESPONSIBILITY: Implements `setup_carbon`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
    printf("Dominium Carbon installer stub.\n");
    printf("TODO: implement Carbon OS TUI to copy binaries/data and register in launcher.\n");
    return 0;
}
