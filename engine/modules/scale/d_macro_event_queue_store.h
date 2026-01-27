/*
Internal macro event queue helpers for engine subsystems.
*/
#ifndef D_MACRO_EVENT_QUEUE_STORE_H
#define D_MACRO_EVENT_QUEUE_STORE_H

#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

void d_macro_event_queue_store_init(d_world* world);
void d_macro_event_queue_store_free(d_world* world);

int d_macro_event_queue_store_serialize(const d_world* world, d_tlv_blob* out_blob);
int d_macro_event_queue_store_deserialize(d_world* world, const d_tlv_blob* in_blob);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_MACRO_EVENT_QUEUE_STORE_H */
