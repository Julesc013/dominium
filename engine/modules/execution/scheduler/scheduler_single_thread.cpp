/*
FILE: source/domino/execution/scheduler/scheduler_single_thread.cpp
MODULE: Domino
RESPONSIBILITY: Reference single-thread deterministic scheduler (EXEC2).
*/
#include "execution/scheduler/scheduler_single_thread.h"

static d_bool task_is_valid(const dom_task_node *node) {
    if (!node) {
        return D_FALSE;
    }
    if (node->category > DOM_TASK_PRESENTATION) {
        return D_FALSE;
    }
    if (node->determinism_class > DOM_DET_DERIVED) {
        return D_FALSE;
    }
    if (node->fidelity_tier > DOM_FID_FOCUS) {
        return D_FALSE;
    }
    if (node->access_set_id == 0u) {
        return D_FALSE;
    }
    if (node->law_scope_ref == 0u) {
        return D_FALSE;
    }
    if (node->category == DOM_TASK_AUTHORITATIVE) {
        if (!node->law_targets || node->law_target_count == 0u) {
            return D_FALSE;
        }
    }
    if (node->commit_key.phase_id != node->phase_id) {
        return D_FALSE;
    }
    if (node->commit_key.task_id != node->task_id) {
        return D_FALSE;
    }
    return D_TRUE;
}

static int find_task_index(const dom_task_graph &graph, u64 task_id) {
    u32 i;
    for (i = 0u; i < graph.task_count; ++i) {
        if (graph.tasks[i].task_id == task_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool graph_has_cycle(const dom_task_graph &graph,
                              const u32 *edge_from,
                              const u32 *edge_to,
                              u32 edge_count) {
    u32 i;
    u32 processed = 0u;
    d_bool *done = 0;
    u32 *indegree = 0;

    if (graph.task_count == 0u) {
        return D_FALSE;
    }
    done = new d_bool[graph.task_count];
    indegree = new u32[graph.task_count];
    for (i = 0u; i < graph.task_count; ++i) {
        done[i] = D_FALSE;
        indegree[i] = 0u;
    }
    for (i = 0u; i < edge_count; ++i) {
        indegree[edge_to[i]] += 1u;
    }
    while (processed < graph.task_count) {
        int next = -1;
        for (i = 0u; i < graph.task_count; ++i) {
            if (!done[i] && indegree[i] == 0u) {
                next = (int)i;
                break;
            }
        }
        if (next < 0) {
            delete[] done;
            delete[] indegree;
            return D_TRUE;
        }
        done[next] = D_TRUE;
        processed += 1u;
        for (i = 0u; i < edge_count; ++i) {
            if (edge_from[i] == (u32)next) {
                indegree[edge_to[i]] -= 1u;
            }
        }
    }
    delete[] done;
    delete[] indegree;
    return D_FALSE;
}

static void record_event(dom_execution_context &ctx,
                         u32 event_id,
                         u64 task_id,
                         u32 decision_kind,
                         u32 refusal_code) {
    dom_audit_event event;
    event.event_id = event_id;
    event.task_id = task_id;
    event.decision_kind = decision_kind;
    event.refusal_code = refusal_code;
    dom_execution_context_record_audit(&ctx, &event);
}

void dom_scheduler_single_thread::schedule(const dom_task_graph &graph,
                                           dom_execution_context &ctx,
                                           IScheduleSink &sink) {
    u32 i;
    u32 phase_start = 0u;
    u32 edge_count = graph.dependency_count;
    u32 *edge_from = 0;
    u32 *edge_to = 0;

    if (!graph.tasks || graph.task_count == 0u) {
        return;
    }
    if (!dom_task_graph_is_sorted(graph.tasks, graph.task_count)) {
        return;
    }
    if (!ctx.lookup_access_set) {
        return;
    }
    for (i = 0u; i < graph.task_count; ++i) {
        if (task_is_valid(&graph.tasks[i]) == D_FALSE) {
            return;
        }
    }
    if (edge_count > 0u && !graph.dependency_edges) {
        return;
    }
    edge_from = new u32[edge_count];
    edge_to = new u32[edge_count];
    for (i = 0u; i < edge_count; ++i) {
        const dom_dependency_edge *edge = &graph.dependency_edges[i];
        int from_index = find_task_index(graph, edge->from_task_id);
        int to_index = find_task_index(graph, edge->to_task_id);
        if (from_index < 0 || to_index < 0) {
            delete[] edge_from;
            delete[] edge_to;
            return;
        }
        if (graph.tasks[from_index].phase_id > graph.tasks[to_index].phase_id) {
            delete[] edge_from;
            delete[] edge_to;
            return;
        }
        edge_from[i] = (u32)from_index;
        edge_to[i] = (u32)to_index;
    }
    if (graph_has_cycle(graph, edge_from, edge_to, edge_count) == D_TRUE) {
        delete[] edge_from;
        delete[] edge_to;
        return;
    }

    while (phase_start < graph.task_count) {
        u32 phase_id = graph.tasks[phase_start].phase_id;
        u32 phase_end = phase_start;
        u32 phase_count;
        u32 *indegree = 0;
        d_bool *scheduled = 0;
        const dom_access_set **phase_access = 0;
        dom_task_node *phase_commits = 0;
        u32 commit_count = 0u;

        while (phase_end < graph.task_count &&
               graph.tasks[phase_end].phase_id == phase_id) {
            phase_end += 1u;
        }
        phase_count = phase_end - phase_start;
        indegree = new u32[phase_count];
        scheduled = new d_bool[phase_count];
        phase_access = new const dom_access_set *[phase_count];
        phase_commits = new dom_task_node[phase_count];

        for (i = 0u; i < phase_count; ++i) {
            indegree[i] = 0u;
            scheduled[i] = D_FALSE;
            phase_access[i] = 0;
        }
        for (i = 0u; i < edge_count; ++i) {
            u32 from_index = edge_from[i];
            u32 to_index = edge_to[i];
            if (from_index >= phase_start && from_index < phase_end &&
                to_index >= phase_start && to_index < phase_end) {
                indegree[to_index - phase_start] += 1u;
            }
        }

        for (i = 0u; i < phase_count; ++i) {
            u32 pick = 0u;
            d_bool found = D_FALSE;
            u32 local_index;
            for (local_index = 0u; local_index < phase_count; ++local_index) {
                if (!scheduled[local_index] && indegree[local_index] == 0u) {
                    pick = local_index;
                    found = D_TRUE;
                    break;
                }
            }
            if (!found) {
                break;
            }

            u32 global_index = phase_start + pick;
            const dom_task_node *orig = &graph.tasks[global_index];
            dom_task_node working;
            dom_law_decision decision;
            const dom_access_set *access = 0;
            d_bool conflict = D_FALSE;

            scheduled[pick] = D_TRUE;
            working = *orig;
            decision = dom_execution_context_evaluate_law(&ctx, &working);
            if (decision.kind == DOM_LAW_TRANSFORM) {
                record_event(ctx, DOM_EXEC_AUDIT_TASK_TRANSFORMED,
                             orig->task_id, decision.kind, decision.refusal_code);
                if (decision.transformed_fidelity_tier <= DOM_FID_FOCUS) {
                    working.fidelity_tier = decision.transformed_fidelity_tier;
                }
                if (decision.transformed_next_due_tick != DOM_EXEC_TICK_INVALID) {
                    working.next_due_tick = decision.transformed_next_due_tick;
                }
                decision = dom_execution_context_evaluate_law(&ctx, &working);
            }

            if (decision.kind == DOM_LAW_REFUSE) {
                record_event(ctx, DOM_EXEC_AUDIT_TASK_REFUSED,
                             orig->task_id, decision.kind,
                             decision.refusal_code ? decision.refusal_code : DOM_EXEC_REFUSE_LAW);
            } else if (decision.kind == DOM_LAW_TRANSFORM) {
                record_event(ctx, DOM_EXEC_AUDIT_TASK_REFUSED,
                             orig->task_id, decision.kind, DOM_EXEC_REFUSE_LAW);
            } else {
                access = dom_execution_context_lookup_access_set(&ctx, working.access_set_id);
                if (!access) {
                    record_event(ctx, DOM_EXEC_AUDIT_TASK_REFUSED,
                                 orig->task_id, DOM_LAW_REFUSE, DOM_EXEC_REFUSE_ACCESS_SET);
                } else if (dom_verify_reduction_rules(access) == D_FALSE) {
                    record_event(ctx, DOM_EXEC_AUDIT_TASK_REFUSED,
                                 orig->task_id, DOM_LAW_REFUSE, DOM_EXEC_REFUSE_REDUCTION);
                } else {
                    u32 c;
                    for (c = 0u; c < commit_count; ++c) {
                        if (dom_detect_access_conflicts(access, phase_access[c]) == D_TRUE) {
                            conflict = D_TRUE;
                            break;
                        }
                    }
                    if (conflict == D_TRUE) {
                        record_event(ctx, DOM_EXEC_AUDIT_TASK_REFUSED,
                                     orig->task_id, DOM_LAW_REFUSE, DOM_EXEC_REFUSE_CONFLICT);
                    } else {
                        record_event(ctx, DOM_EXEC_AUDIT_TASK_ADMITTED,
                                     orig->task_id, decision.kind, 0u);
                        sink.on_task(working, decision);
                        record_event(ctx, DOM_EXEC_AUDIT_TASK_EXECUTED,
                                     orig->task_id, decision.kind, 0u);
                        phase_access[commit_count] = access;
                        phase_commits[commit_count] = working;
                        commit_count += 1u;
                    }
                }
            }

            for (local_index = 0u; local_index < edge_count; ++local_index) {
                u32 from_index = edge_from[local_index];
                u32 to_index = edge_to[local_index];
                if (from_index == global_index &&
                    to_index >= phase_start && to_index < phase_end) {
                    u32 to_local = to_index - phase_start;
                    if (indegree[to_local] > 0u) {
                        indegree[to_local] -= 1u;
                    }
                }
            }
        }

        if (commit_count > 1u) {
            dom_stable_task_sort(phase_commits, commit_count);
        }
        for (i = 0u; i < commit_count; ++i) {
            record_event(ctx, DOM_EXEC_AUDIT_TASK_COMMITTED,
                         phase_commits[i].task_id, DOM_LAW_ACCEPT, 0u);
        }

        delete[] indegree;
        delete[] scheduled;
        delete[] phase_access;
        delete[] phase_commits;
        phase_start = phase_end;
    }

    delete[] edge_from;
    delete[] edge_to;
}
