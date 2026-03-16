Status: DERIVED
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: ABS-3 FlowSystem substrate expansion for deterministic unified flows.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FlowSystem Standard

## Purpose
Define a single deterministic FlowSystem substrate that all quantity transfer domains reuse over `NetworkGraph` without domain-specific solver forks.

## A) FlowChannel
- `FlowChannel` represents a directed transfer of `quantity_id` from `source_node_id` to `sink_node_id` over a `graph_id`.
- Every channel references MAT-1 quantity typing via `quantity_id` and is schema-validated.
- Capacity, delay, loss, priority, and solver policy are explicit channel fields.

## B) Solver Tiers
- Macro (`bulk`): per-tick aggregate transfer with deterministic capacity/delay/loss application.
- Meso (`segmented`): deterministic segmented transfer hooks with per-edge occupancy/state (policy-driven; minimal in this baseline).
- Micro: reserved for ROI-only refinements in future domains; not part of ABS-3 runtime semantics.

## C) Determinism Rules
- Channel processing order: `channel_id` ascending.
- Edge-derived tie-breaks remain deterministic through `NetworkGraph` ordering.
- Budget degradation order: process first `N` channels by `channel_id`, defer remainder.
- No transient state may reorder channels during the same tick.

## D) Ledger Integration
- Conserved quantities must be ledger-accounted:
  - debit source
  - credit sink
- Loss handling for conserved quantities must be explicit:
  - transform into another declared quantity/material, or
  - emit RS-2 exception accounting entry.
- Non-conserved channels (for example signal propagation) may skip ledger debit/credit, but still emit deterministic transfer events.

## E) Partition Awareness
- Cross-shard flow does not mutate remote shards directly.
- Channel ticks may emit a deterministic cross-shard transfer plan artifact when partition metadata is present.
- Plan segmentation is deterministic and replay-safe.

## Refusal Codes
- `refusal.core.flow.invalid`
- `refusal.core.flow.solver_policy_invalid`
- `refusal.core.flow.capacity_insufficient`
- `refusal.core.flow.overflow_refused`

## Migration Rule (MAT-4)
- Logistics manifests remain canonical artifacts.
- Transfer execution must use `FlowChannel` operations in core flow engine.
- Existing manifest lifecycle/refusal semantics are preserved.

## Non-Duplication Rule
- New ad-hoc flow debit/credit loops outside `src/core/flow` are forbidden except RS-2 ledger primitives.
- Domain modules may compose channels and policies, but must not reimplement deterministic flow math.
