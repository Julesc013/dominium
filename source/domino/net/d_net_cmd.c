#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "d_net_cmd.h"

enum {
    D_NET_CMD_MAX_TOTAL     = 8192u,
    D_NET_CMD_MAX_PAYLOAD   = 256u * 1024u
};

static d_net_cmd *g_cmds = (d_net_cmd *)0;
static u32 g_cmd_count = 0u;
static u32 g_cmd_capacity = 0u;

static void d_net_cmd_reset_one(d_net_cmd *cmd) {
    if (!cmd) {
        return;
    }
    cmd->id = 0u;
    cmd->source_peer = 0u;
    cmd->tick = 0u;
    cmd->schema_id = 0u;
    cmd->schema_ver = 0u;
    cmd->_pad0 = 0u;
    cmd->payload.ptr = (unsigned char *)0;
    cmd->payload.len = 0u;
}

void d_net_cmd_free(d_net_cmd *cmd) {
    if (!cmd) {
        return;
    }
    if (cmd->payload.ptr) {
        free(cmd->payload.ptr);
    }
    d_net_cmd_reset_one(cmd);
}

static void d_net_cmd_free_all(void) {
    u32 i;
    for (i = 0u; i < g_cmd_count; ++i) {
        if (g_cmds[i].payload.ptr) {
            free(g_cmds[i].payload.ptr);
        }
        d_net_cmd_reset_one(&g_cmds[i]);
    }
    free(g_cmds);
    g_cmds = (d_net_cmd *)0;
    g_cmd_count = 0u;
    g_cmd_capacity = 0u;
}

static int d_net_cmd_ensure_capacity(u32 needed) {
    u32 new_cap;
    d_net_cmd *new_cmds;
    u32 i;
    if (needed <= g_cmd_capacity) {
        return 0;
    }
    new_cap = g_cmd_capacity ? g_cmd_capacity * 2u : 64u;
    if (new_cap < needed) {
        new_cap = needed;
    }
    if (new_cap > D_NET_CMD_MAX_TOTAL) {
        new_cap = D_NET_CMD_MAX_TOTAL;
    }
    if (needed > new_cap) {
        return -1;
    }
    new_cmds = (d_net_cmd *)realloc(g_cmds, sizeof(d_net_cmd) * new_cap);
    if (!new_cmds) {
        return -1;
    }
    for (i = g_cmd_capacity; i < new_cap; ++i) {
        d_net_cmd_reset_one(&new_cmds[i]);
    }
    g_cmds = new_cmds;
    g_cmd_capacity = new_cap;
    return 0;
}

int d_net_cmd_queue_init(void) {
    d_net_cmd_free_all();
    return 0;
}

void d_net_cmd_queue_shutdown(void) {
    d_net_cmd_free_all();
}

static u32 d_net_cmd_count_for_tick(u32 tick) {
    u32 i;
    u32 count = 0u;
    for (i = 0u; i < g_cmd_count; ++i) {
        if (g_cmds[i].tick == tick) {
            count += 1u;
        }
    }
    return count;
}

int d_net_cmd_enqueue(const d_net_cmd *cmd) {
    unsigned char *payload_copy;
    u32 per_tick;
    if (!cmd) {
        return -1;
    }
    if (cmd->schema_id == 0u || cmd->schema_ver == 0u) {
        return -2;
    }
    if (cmd->payload.len > 0u && !cmd->payload.ptr) {
        return -3;
    }
    if (cmd->payload.len > D_NET_CMD_MAX_PAYLOAD) {
        return -4;
    }

    if (g_cmd_count >= D_NET_CMD_MAX_TOTAL) {
        fprintf(stderr, "d_net_cmd_enqueue: queue full\n");
        return -5;
    }

    per_tick = d_net_cmd_count_for_tick(cmd->tick);
    if (per_tick >= D_NET_CMD_MAX_PER_TICK) {
        fprintf(stderr, "d_net_cmd_enqueue: per-tick limit reached (tick=%u)\n",
                (unsigned int)cmd->tick);
        return -6;
    }

    if (d_net_cmd_ensure_capacity(g_cmd_count + 1u) != 0) {
        return -7;
    }

    payload_copy = (unsigned char *)0;
    if (cmd->payload.len > 0u) {
        payload_copy = (unsigned char *)malloc(cmd->payload.len);
        if (!payload_copy) {
            return -8;
        }
        memcpy(payload_copy, cmd->payload.ptr, cmd->payload.len);
    }

    g_cmds[g_cmd_count] = *cmd;
    g_cmds[g_cmd_count].payload.ptr = payload_copy;
    g_cmd_count += 1u;
    return 0;
}

int d_net_cmd_dequeue_for_tick(
    u32       tick,
    d_net_cmd *out_cmd,
    u32       max_cmds,
    u32      *out_count
) {
    u32 i;
    u32 out_n = 0u;

    if (!out_count) {
        return -1;
    }
    *out_count = 0u;
    if (max_cmds > 0u && !out_cmd) {
        return -1;
    }

    /* Move matching commands into out_cmd, transferring payload ownership. */
    i = 0u;
    while (i < g_cmd_count) {
        if (g_cmds[i].tick != tick) {
            i += 1u;
            continue;
        }
        if (out_n >= max_cmds) {
            fprintf(stderr, "d_net_cmd_dequeue_for_tick: output too small for tick %u\n",
                    (unsigned int)tick);
            return -2;
        }

        out_cmd[out_n] = g_cmds[i];
        d_net_cmd_reset_one(&g_cmds[i]);
        out_n += 1u;

        /* Remove by swapping with last. */
        g_cmd_count -= 1u;
        if (i != g_cmd_count) {
            g_cmds[i] = g_cmds[g_cmd_count];
            d_net_cmd_reset_one(&g_cmds[g_cmd_count]);
        } else {
            d_net_cmd_reset_one(&g_cmds[g_cmd_count]);
        }
    }

    *out_count = out_n;
    return 0;
}
