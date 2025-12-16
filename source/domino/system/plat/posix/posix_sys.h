/*
FILE: source/domino/system/plat/posix/posix_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/posix/posix_sys
RESPONSIBILITY: Implements `posix_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_POSIX_SYS_H
#define DOMINO_POSIX_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <dirent.h>
#include <unistd.h>

struct dsys_window_t {
    int dummy; /* no windows */
};

struct dsys_dir_iter_t {
    DIR* dir;
};

struct dsys_process_t {
    pid_t pid;
};

const dsys_backend_vtable* dsys_posix_get_vtable(void);

#endif /* DOMINO_POSIX_SYS_H */
