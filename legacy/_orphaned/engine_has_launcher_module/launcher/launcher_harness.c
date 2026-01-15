/*
FILE: source/domino/launcher/launcher_harness.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / launcher/launcher_harness
RESPONSIBILITY: Implements `launcher_harness`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/launcher.h"

int main(int argc, char** argv)
{
    launcher_config cfg;
    (void)argc;
    (void)argv;

    launcher_config_load(&cfg);
    if (launcher_init(&cfg) != 0) {
        return 1;
    }
    launcher_run();
    launcher_shutdown();
    return 0;
}
