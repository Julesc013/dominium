/*
FILE: source/domino/sys/thread_pool.h
MODULE: Domino
RESPONSIBILITY: Deterministic fixed-size thread pool.
*/
#ifndef DOM_SYS_THREAD_POOL_H
#define DOM_SYS_THREAD_POOL_H

#include "sys/work_steal_deque.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
typedef HANDLE dom_thread;
typedef CONDITION_VARIABLE dom_cond;
#else
#include <pthread.h>
typedef pthread_t dom_thread;
typedef pthread_cond_t dom_cond;
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_thread_pool_worker dom_thread_pool_worker;

typedef struct dom_thread_pool {
    dom_thread_pool_worker *workers;
    u32 worker_count;
    u32 queue_capacity;
    dom_mutex mutex;
    dom_cond cond;
    d_bool shutting_down;
    u32 active_tasks;
    u32 next_submit;
} dom_thread_pool;

d_bool dom_thread_pool_init(dom_thread_pool *pool, u32 worker_count, u32 queue_capacity);
void dom_thread_pool_shutdown(dom_thread_pool *pool);

d_bool dom_thread_pool_submit(dom_thread_pool *pool, const dom_thread_pool_task *task);
d_bool dom_thread_pool_submit_to(dom_thread_pool *pool,
                                const dom_thread_pool_task *task,
                                u32 worker_index);
void dom_thread_pool_wait(dom_thread_pool *pool);

void dom_cond_init(dom_cond *c);
void dom_cond_destroy(dom_cond *c);
void dom_cond_wait(dom_cond *c, dom_mutex *m);
void dom_cond_signal(dom_cond *c);
void dom_cond_broadcast(dom_cond *c);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SYS_THREAD_POOL_H */
