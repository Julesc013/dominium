Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# AI Autonomy Baseline (T24)

Status: binding.  
Scope: AI-native goals, delegation contracts, and deterministic planning.

## What exists now
- AI goals are explicit, inspectable artifacts with priorities and expiry.
- Delegation contracts define allowed process families and budgets.
- Planning is deterministic, bounded, and replayable.
- Plans are explainable and fail for visible reasons.
- Oversight can pause, approve, or revoke delegated autonomy.

## What does NOT exist yet
- Nondeterministic ML inference or opaque planners.
- Global, omniscient scheduling or “god-mode” AI.
- AI-only capabilities that bypass law, energy, or knowledge constraints.
- Per-tick global AI simulation loops.

## How it works (baseline)
1. Goals are registered in data with constraints and priority.
2. Delegations grant limited autonomy and budgets.
3. Deterministic planning produces a plan graph under budget.
4. Execution submits normal processes and handles refusals.
5. Oversight can intervene at any point, leaving a replayable trace.

## Why AI fails realistically
- Budgets run out (time, energy, risk).
- Knowledge is incomplete or incorrect.
- Plans are bounded and may be suboptimal.
- Refusals propagate back to the planner.

## Scaling and determinism
- Planning cost is bounded by autonomy budget.
- Inactive AI incurs no cost.
- Collapse/expand preserves summary statistics and RNG cursor continuity.
- Replays reproduce identical decisions and failures.

## Forward compatibility
This baseline supports future layers:
- richer job graphs and institutional workflows
- audit-driven trust updates
- delegation markets and governance constraints

## See also
- `docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`