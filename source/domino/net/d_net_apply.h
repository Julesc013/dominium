/* Deterministic net command application (C89). */
#ifndef D_NET_APPLY_H
#define D_NET_APPLY_H

#include "domino/core/types.h"
#include "net/d_net_cmd.h"

struct d_world;

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*d_net_tick_cmds_observer_fn)(
    void          *user,
    struct d_world *w,
    u32            tick,
    const d_net_cmd *cmds,
    u32            cmd_count
);

void d_net_set_tick_cmds_observer(d_net_tick_cmds_observer_fn fn, void *user);
int d_net_apply_for_tick(struct d_world *w, u32 tick);

#ifdef __cplusplus
}
#endif

#endif /* D_NET_APPLY_H */
