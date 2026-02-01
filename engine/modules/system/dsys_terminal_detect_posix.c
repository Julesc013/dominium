/*
FILE: source/domino/system/dsys_terminal_detect_posix.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_terminal_detect_posix
RESPONSIBILITY: Implements `dsys_terminal_detect_posix`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/system/dsys.h"

#include <unistd.h>

int dsys_running_in_terminal(void)
{
    int tty_in  = isatty(0); /* STDIN_FILENO */
    int tty_out = isatty(1); /* STDOUT_FILENO */
    return (tty_in || tty_out) ? 1 : 0;
}
