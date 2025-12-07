#include "dom_draw_common.h"

void dom_draw_cmd_buffer_init(DomDrawCommandBuffer *cb)
{
    if (!cb) {
        return;
    }
    cb->count = 0;
}

dom_err_t dom_draw_cmd_buffer_push(DomDrawCommandBuffer *cb,
                                   const DomDrawCommand *cmd)
{
    if (!cb || !cmd) {
        return DOM_ERR_INVALID_ARG;
    }
    if (cb->count >= DOM_DRAW_COMMAND_MAX) {
        return DOM_ERR_OVERFLOW;
    }
    cb->cmds[cb->count] = *cmd;
    cb->count += 1;
    return DOM_OK;
}

/* Optional stable depth sort for triangle commands (back-to-front). */
void dom_draw_cmd_buffer_sort_triangles(DomDrawCommandBuffer *cb)
{
    dom_u32 i;
    dom_u32 j;
    if (!cb) {
        return;
    }
    for (i = 1; i < cb->count; ++i) {
        DomDrawCommand key = cb->cmds[i];
        dom_i64 key_depth = 0;
        dom_bool8 is_tri = (key.type == DOM_CMD_TRIANGLE);
        if (is_tri) {
            key_depth = (dom_i64)key.u.tri.z0 +
                        (dom_i64)key.u.tri.z1 +
                        (dom_i64)key.u.tri.z2;
        }
        j = i;
        while (j > 0) {
            dom_bool8 swap = 0;
            if (cb->cmds[j - 1].type == DOM_CMD_TRIANGLE && is_tri) {
                dom_i64 prev_depth = (dom_i64)cb->cmds[j - 1].u.tri.z0 +
                                     (dom_i64)cb->cmds[j - 1].u.tri.z1 +
                                     (dom_i64)cb->cmds[j - 1].u.tri.z2;
                if (prev_depth < key_depth) {
                    swap = 1;
                }
            }
            if (!swap) {
                break;
            }
            cb->cmds[j] = cb->cmds[j - 1];
            j -= 1;
        }
        cb->cmds[j] = key;
    }
}
