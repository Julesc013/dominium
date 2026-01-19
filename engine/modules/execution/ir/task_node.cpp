/*
FILE: source/domino/execution/ir/task_node.cpp
MODULE: Domino
RESPONSIBILITY: TaskNode helpers for deterministic ordering.
*/
#include "domino/execution/task_node.h"

int dom_commit_key_compare(const dom_commit_key *a, const dom_commit_key *b) {
    if (a == b) {
        return 0;
    }
    if (!a) {
        return -1;
    }
    if (!b) {
        return 1;
    }
    if (a->phase_id < b->phase_id) return -1;
    if (a->phase_id > b->phase_id) return 1;
    if (a->task_id < b->task_id) return -1;
    if (a->task_id > b->task_id) return 1;
    if (a->sub_index < b->sub_index) return -1;
    if (a->sub_index > b->sub_index) return 1;
    return 0;
}

int dom_task_node_compare(const dom_task_node *a, const dom_task_node *b) {
    if (a == b) {
        return 0;
    }
    if (!a) {
        return -1;
    }
    if (!b) {
        return 1;
    }
    return dom_commit_key_compare(&a->commit_key, &b->commit_key);
}
