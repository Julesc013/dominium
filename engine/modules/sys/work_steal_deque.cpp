/*
FILE: source/domino/sys/work_steal_deque.cpp
MODULE: Domino
RESPONSIBILITY: Work-stealing deque (deterministic, lock-protected).
*/
#include "sys/work_steal_deque.h"

void dom_mutex_init(dom_mutex *m) {
#ifdef _WIN32
    InitializeCriticalSection(m);
#else
    (void)pthread_mutex_init(m, 0);
#endif
}

void dom_mutex_destroy(dom_mutex *m) {
#ifdef _WIN32
    DeleteCriticalSection(m);
#else
    (void)pthread_mutex_destroy(m);
#endif
}

void dom_mutex_lock(dom_mutex *m) {
#ifdef _WIN32
    EnterCriticalSection(m);
#else
    (void)pthread_mutex_lock(m);
#endif
}

void dom_mutex_unlock(dom_mutex *m) {
#ifdef _WIN32
    LeaveCriticalSection(m);
#else
    (void)pthread_mutex_unlock(m);
#endif
}

static u32 next_index(u32 index, u32 capacity) {
    return (index + 1u) % capacity;
}

d_bool dom_ws_deque_init(dom_ws_deque *dq, u32 capacity) {
    if (!dq || capacity == 0u) {
        return D_FALSE;
    }
    dq->items = new dom_thread_pool_task[capacity];
    dq->capacity = capacity;
    dq->top = 0u;
    dq->bottom = 0u;
    dom_mutex_init(&dq->mutex);
    return D_TRUE;
}

void dom_ws_deque_free(dom_ws_deque *dq) {
    if (!dq) {
        return;
    }
    dom_mutex_destroy(&dq->mutex);
    delete[] dq->items;
    dq->items = 0;
    dq->capacity = 0u;
    dq->top = 0u;
    dq->bottom = 0u;
}

d_bool dom_ws_deque_is_empty(dom_ws_deque *dq) {
    d_bool empty;
    if (!dq) {
        return D_TRUE;
    }
    dom_mutex_lock(&dq->mutex);
    empty = (dq->top == dq->bottom) ? D_TRUE : D_FALSE;
    dom_mutex_unlock(&dq->mutex);
    return empty;
}

d_bool dom_ws_deque_push_bottom(dom_ws_deque *dq, const dom_thread_pool_task *task) {
    d_bool ok = D_FALSE;
    u32 next;
    if (!dq || !task) {
        return D_FALSE;
    }
    dom_mutex_lock(&dq->mutex);
    next = next_index(dq->bottom, dq->capacity);
    if (next != dq->top) {
        dq->items[dq->bottom] = *task;
        dq->bottom = next;
        ok = D_TRUE;
    }
    dom_mutex_unlock(&dq->mutex);
    return ok;
}

d_bool dom_ws_deque_pop_bottom(dom_ws_deque *dq, dom_thread_pool_task *out_task) {
    d_bool ok = D_FALSE;
    if (!dq || !out_task) {
        return D_FALSE;
    }
    dom_mutex_lock(&dq->mutex);
    if (dq->top != dq->bottom) {
        u32 new_bottom = (dq->bottom == 0u) ? (dq->capacity - 1u) : (dq->bottom - 1u);
        dq->bottom = new_bottom;
        *out_task = dq->items[new_bottom];
        ok = D_TRUE;
    }
    dom_mutex_unlock(&dq->mutex);
    return ok;
}

d_bool dom_ws_deque_steal_top(dom_ws_deque *dq, dom_thread_pool_task *out_task) {
    d_bool ok = D_FALSE;
    if (!dq || !out_task) {
        return D_FALSE;
    }
    dom_mutex_lock(&dq->mutex);
    if (dq->top != dq->bottom) {
        *out_task = dq->items[dq->top];
        dq->top = next_index(dq->top, dq->capacity);
        ok = D_TRUE;
    }
    dom_mutex_unlock(&dq->mutex);
    return ok;
}
