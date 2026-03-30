Status: DERIVED
Last Reviewed: 2026-03-31
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot reconciliation guidance after fresh repository archaeology

# Repo Reality Reconciliation Guide

## Reconciliation Rules

| Rule | Statement | Preferred Action | Escalation |
| --- | --- | --- | --- |
| reality.extend_existing | If the live repo already has a subsystem that satisfies the blueprint, prefer extending it. | keep | Extend the existing subsystem instead of rebuilding the idea from scratch. |
| reality.route_duplicates_through_xi | If duplicate implementations exist, route through XI-series convergence logic first. | merge | Use XI evidence to converge duplicate or overlapping implementations before future work starts. |
| reality.code_beats_docs | If documentation contradicts code, code is authoritative until reconciled. | reconcile | Update docs, registries, or blueprint assumptions so the code and plan agree again. |
| reality.unknown_boundary_means_post_snapshot | If the blueprint assumes a module boundary not present in repo, mark it as post-snapshot-required. | replace | Mark the blueprint assumption as post-snapshot-required and derive a repo-specific replacement strategy. |
| reality.extend_before_invent | Never invent new modules if an existing module can be extended safely. | keep | Extend the existing subsystem instead of rebuilding the idea from scratch. |
| reality.uncertainty_quarantines | If uncertain, quarantine and escalate to manual review. | quarantine | Create a manual review packet and stop implementation planning until the ambiguity is resolved. |

## Decision Outcomes

- `keep`
- `merge`
- `replace`
- `discard`
- `quarantine`
