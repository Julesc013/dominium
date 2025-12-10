#include "domino/state/state.h"

void d_state_machine_init(d_state_machine* sm,
                          d_state* states,
                          u32 count,
                          void* userdata) {
    if (!sm) {
        return;
    }
    sm->states = states;
    sm->count = count;
    sm->userdata = userdata;
    sm->current = count; /* invalid sentinel until set */
}

void d_state_machine_update(d_state_machine* sm) {
    const d_state* st;
    if (!sm || !sm->states) {
        return;
    }
    if (sm->current >= sm->count) {
        return;
    }
    st = &sm->states[sm->current];
    if (st->on_update) {
        st->on_update(sm->userdata);
    }
}

void d_state_machine_set(d_state_machine* sm, u32 index) {
    const d_state* st;
    if (!sm || !sm->states) {
        return;
    }
    if (index >= sm->count) {
        return;
    }
    if (sm->current == index) {
        return;
    }
    if (sm->current < sm->count) {
        st = &sm->states[sm->current];
        if (st->on_exit) {
            st->on_exit(sm->userdata);
        }
    }
    sm->current = index;
    st = &sm->states[sm->current];
    if (st->on_enter) {
        st->on_enter(sm->userdata);
    }
}
