/*
FILE: source/domino/sys/thread_pool.cpp
MODULE: Domino
RESPONSIBILITY: Deterministic fixed-size thread pool.
*/
#include "sys/thread_pool.h"

typedef struct dom_thread_pool_worker {
    dom_thread thread;
    u32 index;
    dom_thread_pool *pool;
    dom_ws_deque deque;
} dom_thread_pool_worker;

void dom_cond_init(dom_cond *c) {
#ifdef _WIN32
    InitializeConditionVariable(c);
#else
    (void)pthread_cond_init(c, 0);
#endif
}

void dom_cond_destroy(dom_cond *c) {
#ifdef _WIN32
    (void)c;
#else
    (void)pthread_cond_destroy(c);
#endif
}

void dom_cond_wait(dom_cond *c, dom_mutex *m) {
#ifdef _WIN32
    SleepConditionVariableCS(c, m, INFINITE);
#else
    (void)pthread_cond_wait(c, m);
#endif
}

void dom_cond_signal(dom_cond *c) {
#ifdef _WIN32
    WakeConditionVariable(c);
#else
    (void)pthread_cond_signal(c);
#endif
}

void dom_cond_broadcast(dom_cond *c) {
#ifdef _WIN32
    WakeAllConditionVariable(c);
#else
    (void)pthread_cond_broadcast(c);
#endif
}

static d_bool pool_has_pending(dom_thread_pool *pool) {
    return (pool->active_tasks > 0u) ? D_TRUE : D_FALSE;
}

static d_bool pool_try_steal(dom_thread_pool *pool,
                             u32 thief_index,
                             dom_thread_pool_task *out_task) {
    u32 i;
    if (!pool || !out_task) {
        return D_FALSE;
    }
    for (i = 0u; i < pool->worker_count; ++i) {
        u32 idx = (thief_index + 1u + i) % pool->worker_count;
        if (idx == thief_index) {
            continue;
        }
        if (dom_ws_deque_steal_top(&pool->workers[idx].deque, out_task) == D_TRUE) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

#ifdef _WIN32
static DWORD WINAPI dom_thread_pool_entry(LPVOID arg)
#else
static void *dom_thread_pool_entry(void *arg)
#endif
{
    dom_thread_pool_worker *worker = (dom_thread_pool_worker *)arg;
    dom_thread_pool *pool = worker ? worker->pool : 0;
    dom_thread_pool_task task;

    if (!worker || !pool) {
#ifdef _WIN32
        return 0;
#else
        return 0;
#endif
    }

    for (;;) {
        d_bool got = D_FALSE;
        if (dom_ws_deque_pop_bottom(&worker->deque, &task) == D_TRUE) {
            got = D_TRUE;
        } else if (pool_try_steal(pool, worker->index, &task) == D_TRUE) {
            got = D_TRUE;
        }

        if (got == D_TRUE) {
            if (task.fn) {
                task.fn(task.user_data);
            }
            dom_mutex_lock(&pool->mutex);
            if (pool->active_tasks > 0u) {
                pool->active_tasks -= 1u;
            }
            if (pool->active_tasks == 0u) {
                dom_cond_broadcast(&pool->cond);
            }
            dom_mutex_unlock(&pool->mutex);
            continue;
        }

        dom_mutex_lock(&pool->mutex);
        while (pool->shutting_down == D_FALSE && pool_has_pending(pool) == D_FALSE) {
            dom_cond_wait(&pool->cond, &pool->mutex);
        }
        if (pool->shutting_down == D_TRUE) {
            dom_mutex_unlock(&pool->mutex);
            break;
        }
        dom_mutex_unlock(&pool->mutex);
    }

#ifdef _WIN32
    return 0;
#else
    return 0;
#endif
}

d_bool dom_thread_pool_init(dom_thread_pool *pool, u32 worker_count, u32 queue_capacity) {
    u32 i;
    if (!pool || worker_count == 0u) {
        return D_FALSE;
    }
    pool->workers = new dom_thread_pool_worker[worker_count];
    pool->worker_count = worker_count;
    pool->queue_capacity = queue_capacity == 0u ? 1u : queue_capacity;
    pool->shutting_down = D_FALSE;
    pool->active_tasks = 0u;
    pool->next_submit = 0u;
    dom_mutex_init(&pool->mutex);
    dom_cond_init(&pool->cond);

    for (i = 0u; i < worker_count; ++i) {
        dom_thread_pool_worker *w = &pool->workers[i];
        w->index = i;
        w->pool = pool;
        if (dom_ws_deque_init(&w->deque, pool->queue_capacity) == D_FALSE) {
            return D_FALSE;
        }
#ifdef _WIN32
        w->thread = CreateThread(0, 0, dom_thread_pool_entry, w, 0, 0);
        if (!w->thread) {
            return D_FALSE;
        }
#else
        if (pthread_create(&w->thread, 0, dom_thread_pool_entry, w) != 0) {
            return D_FALSE;
        }
#endif
    }
    return D_TRUE;
}

void dom_thread_pool_shutdown(dom_thread_pool *pool) {
    u32 i;
    if (!pool || !pool->workers) {
        return;
    }
    dom_mutex_lock(&pool->mutex);
    pool->shutting_down = D_TRUE;
    dom_cond_broadcast(&pool->cond);
    dom_mutex_unlock(&pool->mutex);

    for (i = 0u; i < pool->worker_count; ++i) {
#ifdef _WIN32
        WaitForSingleObject(pool->workers[i].thread, INFINITE);
        CloseHandle(pool->workers[i].thread);
#else
        (void)pthread_join(pool->workers[i].thread, 0);
#endif
        dom_ws_deque_free(&pool->workers[i].deque);
    }

    delete[] pool->workers;
    pool->workers = 0;
    pool->worker_count = 0u;
    dom_mutex_destroy(&pool->mutex);
    dom_cond_destroy(&pool->cond);
}

d_bool dom_thread_pool_submit_to(dom_thread_pool *pool,
                                const dom_thread_pool_task *task,
                                u32 worker_index) {
    d_bool ok = D_FALSE;
    if (!pool || !task || !pool->workers || pool->worker_count == 0u) {
        return D_FALSE;
    }
    worker_index = worker_index % pool->worker_count;
    if (dom_ws_deque_push_bottom(&pool->workers[worker_index].deque, task) == D_TRUE) {
        dom_mutex_lock(&pool->mutex);
        pool->active_tasks += 1u;
        dom_cond_signal(&pool->cond);
        dom_mutex_unlock(&pool->mutex);
        ok = D_TRUE;
    }
    return ok;
}

d_bool dom_thread_pool_submit(dom_thread_pool *pool, const dom_thread_pool_task *task) {
    d_bool ok;
    u32 worker_index;
    if (!pool) {
        return D_FALSE;
    }
    worker_index = pool->next_submit;
    pool->next_submit = (pool->next_submit + 1u) % pool->worker_count;
    ok = dom_thread_pool_submit_to(pool, task, worker_index);
    return ok;
}

void dom_thread_pool_wait(dom_thread_pool *pool) {
    if (!pool) {
        return;
    }
    dom_mutex_lock(&pool->mutex);
    while (pool->active_tasks > 0u) {
        dom_cond_wait(&pool->cond, &pool->mutex);
    }
    dom_mutex_unlock(&pool->mutex);
}
