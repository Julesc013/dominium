#include "dom_sprite_batch.h"

void dom_sprite_batch_init(DomSpriteBatch *batch)
{
    if (!batch) {
        return;
    }
    dom_draw_cmd_buffer_init(&batch->buffer);
}

dom_err_t dom_sprite_batch_push(DomSpriteBatch *batch,
                                const DomDrawCommand *cmd)
{
    if (!batch) {
        return DOM_ERR_INVALID_ARG;
    }
    return dom_draw_cmd_buffer_push(&batch->buffer, cmd);
}

const DomDrawCommandBuffer *dom_sprite_batch_commands(const DomSpriteBatch *batch)
{
    if (!batch) {
        return 0;
    }
    return &batch->buffer;
}
