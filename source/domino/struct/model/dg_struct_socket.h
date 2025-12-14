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

