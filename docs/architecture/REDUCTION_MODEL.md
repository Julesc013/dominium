Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Reduction Model (DETER-0)

Status: binding.
Scope: deterministic reductions in authoritative code paths.

## Core rule
All authoritative reductions MUST be performed in a fixed, deterministic order.
Parallel execution may compute partial results, but merge order MUST be
independent of thread completion order.

This document complements (and does not replace)
`docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`. The fixed-tree requirement
from that document remains mandatory; the helpers below provide the canonical
ordering and merge utilities used to implement those fixed trees.

## Canonical reduction workflow
1. Emit partials as `(key, value)` items with deterministic keys.
2. Sort items by key using `dom_det_order_sort` (or helpers built on it).
3. Reduce using a fixed tree whose input order is the sorted key order.

## Canonical helper API (required)
Authoritative reductions MUST use:
- `dom_det_reduce_sort_*`
- `dom_det_reduce_sum_*`
- `dom_det_reduce_min_*`
- `dom_det_reduce_max_*`
- `dom_det_reduce_hist_merge`
- `dom_det_reduce_dist_merge`

These helpers provide deterministic ordering and stable merge behavior.

## Forbidden
- Order-dependent reductions (e.g., unordered map iteration).
- Thread-completion-order merges.
- Floating-point reduction in authoritative paths.

## See also
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`