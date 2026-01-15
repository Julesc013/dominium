/*
FILE: source/domino/struct/model/dg_struct_socket.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_socket
RESPONSIBILITY: Defines internal contract for `dg_struct_socket`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT sockets (C89).
 *
 * Sockets are authored attachment points with local parameterization. They are
 * used as hosts for other subsystems (DECOR/AGENT/SYSTEMS) via anchor kinds.
 */
#ifndef DG_STRUCT_SOCKET_H
#define DG_STRUCT_SOCKET_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "struct/model/dg_struct_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_struct_socket {
    dg_struct_socket_id          id;
    dg_struct_surface_template_id surface_template_id; /* attachment host */

    /* Surface parameterization (u,v) plus offset along surface normal. */
    dg_q u;
    dg_q v;
    dg_q offset;
} dg_struct_socket;

void dg_struct_socket_clear(dg_struct_socket *s);
int  dg_struct_socket_validate(const dg_struct_socket *s);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_SOCKET_H */

