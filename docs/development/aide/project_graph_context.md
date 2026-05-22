Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# AIDE Project Graph Context

AIDE and Codex may use project graph facts to select context, summarize provenance, identify likely validators, and route follow-up tasks. The graph is a derived map over repo truth and cannot expand a task beyond explicit allowed paths, scope, non-goals, or review gates.

AIDE task routing must preserve `source_ref` and evidence references when it cites graph facts. If a graph query is incomplete, AIDE should carry the incomplete reason into the task packet rather than treating absence as proof. Mechanical blockers may be resolved through explicit follow-up tasks, but graph facts alone do not authorize runtime, release, Workbench, package, or gameplay implementation.
