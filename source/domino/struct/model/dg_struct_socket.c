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

