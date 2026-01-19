/*
FILE: source/domino/execution/ir/task_graph.cpp
MODULE: Domino
RESPONSIBILITY: TaskGraph helpers for deterministic ordering.
*/
#include "domino/execution/task_graph.h"

void dom_stable_task_sort(dom_task_node *tasks, u32 task_count) {
    u32 i;
    if (!tasks || task_count < 2u) {
        return;
    }
    for (i = 1u; i < task_count; ++i) {
        dom_task_node key = tasks[i];
        u32 j = i;
        while (j > 0u) {
            const dom_task_node *prev = &tasks[j - 1u];
            if (dom_task_node_compare(prev, &key) <= 0) {
                break;
            }
            tasks[j] = tasks[j - 1u];
            --j;
        }
        tasks[j] = key;
    }
}

d_bool dom_task_graph_is_sorted(const dom_task_node *tasks, u32 task_count) {
    u32 i;
    if (!tasks || task_count < 2u) {
        return D_TRUE;
    }
    for (i = 1u; i < task_count; ++i) {
        if (dom_task_node_compare(&tasks[i - 1u], &tasks[i]) > 0) {
            return D_FALSE;
        }
    }
    return D_TRUE;
}
