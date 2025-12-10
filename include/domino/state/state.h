#ifndef DOMINO_STATE_STATE_H
#define DOMINO_STATE_STATE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_state {
    void (*on_enter)(void* userdata);
    void (*on_update)(void* userdata);
    void (*on_exit)(void* userdata);
} d_state;

typedef struct d_state_machine {
    u32      current;
    d_state* states;
    u32      count;
    void*    userdata;
} d_state_machine;

void d_state_machine_init(d_state_machine* sm,
                          d_state* states,
                          u32 count,
                          void* userdata);
void d_state_machine_update(d_state_machine* sm);
void d_state_machine_set(d_state_machine* sm, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_STATE_STATE_H */
