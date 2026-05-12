/*
FILE: source/domino/struct/model/dg_struct_socket.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_socket
RESPONSIBILITY: Implements `dg_struct_socket`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT sockets (C89). */
#include "struct/model/dg_struct_socket.h"

#include <string.h>

void dg_struct_socket_clear(dg_struct_socket *s) {
    if (!s) return;
    memset(s, 0, sizeof(*s));
}

int dg_struct_socket_validate(const dg_struct_socket *s) {
    if (!s) return -1;
    if (s->id == 0u) return -2;
    if (s->surface_template_id == 0u) return -3;
    return 0;
}

