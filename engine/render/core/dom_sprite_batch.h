#ifndef DOM_SPRITE_BATCH_H
#define DOM_SPRITE_BATCH_H

#include "dom_draw_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct DomSpriteBatch {
    DomDrawCommandBuffer buffer;
} DomSpriteBatch;

void dom_sprite_batch_init(DomSpriteBatch *batch);
dom_err_t dom_sprite_batch_push(DomSpriteBatch *batch,
                                const DomDrawCommand *cmd);
const DomDrawCommandBuffer *dom_sprite_batch_commands(const DomSpriteBatch *batch);

#ifdef __cplusplus
}
#endif

#endif /* DOM_SPRITE_BATCH_H */
