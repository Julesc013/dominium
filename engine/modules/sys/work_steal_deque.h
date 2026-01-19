/*
FILE: source/domino/sys/work_steal_deque.h
MODULE: Domino
RESPONSIBILITY: Work-stealing deque (deterministic, lock-protected).
*/
#ifndef DOM_SYS_WORK_STEAL_DEQUE_H
#define DOM_SYS_WORK_STEAL_DEQUE_H

#include "domino/core/types.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
typedef CRITICAL_SECTION dom_mutex;
#else
#include <pthread.h>
typedef pthread_mutex_t dom_mutex;
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*dom_thread_task_fn)(void *user_data);

typedef struct dom_thread_pool_task {
    u64 task_id;
    dom_thread_task_fn fn;
    void *user_data;
} dom_thread_pool_task;

typedef struct dom_ws_deque {
    dom_thread_pool_task *items;
    u32 capacity;
    u32 top;
    u32 bottom;
    dom_mutex mutex;
} dom_ws_deque;

void dom_mutex_init(dom_mutex *m);
void dom_mutex_destroy(dom_mutex *m);
void dom_mutex_lock(dom_mutex *m);
void dom_mutex_unlock(dom_mutex *m);

d_bool dom_ws_deque_init(dom_ws_deque *dq, u32 capacity);
void dom_ws_deque_free(dom_ws_deque *dq);

d_bool dom_ws_deque_push_bottom(dom_ws_deque *dq, const dom_thread_pool_task *task);
d_bool dom_ws_deque_pop_bottom(dom_ws_deque *dq, dom_thread_pool_task *out_task);
d_bool dom_ws_deque_steal_top(dom_ws_deque *dq, dom_thread_pool_task *out_task);
d_bool dom_ws_deque_is_empty(dom_ws_deque *dq);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SYS_WORK_STEAL_DEQUE_H */
